"""Local browser review inbox for exact ASCII style samples.

Run:
    python review_app.py
    python review_app.py --enable-git-publish

The server binds to loopback by default. Decisions and corrections are written
inside style_samples/ without promoting golden targets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import threading
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


CATALOG_PATH = Path("style_samples/catalog_v2.json")
DECISIONS_DIR = Path("style_samples/decisions")
CORRECTIONS_DIR = Path("style_samples/corrections")
HTML_PATH = Path("review_app.html")
GRID_EDITOR_PATH = Path("review_grid_editor.js")
MAX_BODY_BYTES = 2 * 1024 * 1024
VALID_DECISIONS = frozenset({"approved", "rejected", "needs_changes", "skipped"})
SAFE_SAMPLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ARTWORK_HEADINGS = (
    "USER-AUTHORED PROJECTION",
    "AUTOMATIC DRAFT",
    "REVISED DRAFT",
    "REFERENCE PROJECTION",
    "CURRENT GENERATED ARTWORK",
    "APPROVED PROJECTION",
    "PROJECTION",
    "RENDERING",
)


class ReviewError(RuntimeError):
    """Base class for review-app errors."""


class NotFoundError(ReviewError):
    """Requested sample or file does not exist."""


class ValidationError(ReviewError):
    """Submitted review data is invalid."""


class StaleCandidateError(ReviewError):
    """A decision references a candidate that has since changed."""


class PublishError(ReviewError):
    """The optional git publishing operation could not be completed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_sample_id(sample_id: str) -> str:
    if not SAFE_SAMPLE_ID.fullmatch(sample_id):
        raise ValidationError("Invalid sample id.")
    return sample_id


def safe_project_path(root: Path, relative: str | Path) -> Path:
    rel = Path(relative)
    if rel.is_absolute():
        raise ValidationError("Absolute paths are not allowed.")
    root_resolved = root.resolve()
    candidate = (root_resolved / rel).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ValidationError("Path escapes the project root.") from exc
    return candidate


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _is_underline(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and set(stripped) <= {"-", "="}


def extract_artwork(raw_text: str) -> str:
    """Extract the exact artwork block from a metadata-wrapped review file.

    Raw target files are returned unchanged. Review files use a heading followed
    by an underline and a contiguous artwork block.
    """

    lines = raw_text.splitlines()
    for heading in ARTWORK_HEADINGS:
        for index, line in enumerate(lines):
            if line.strip().upper() != heading:
                continue
            cursor = index + 1
            if cursor < len(lines) and _is_underline(lines[cursor]):
                cursor += 1
            while cursor < len(lines) and lines[cursor] == "":
                cursor += 1
            artwork: list[str] = []
            while cursor < len(lines) and lines[cursor] != "":
                artwork.append(lines[cursor])
                cursor += 1
            if artwork:
                return "\n".join(artwork) + "\n"
    return raw_text


def row_lengths(text: str) -> list[int]:
    return [len(line) for line in text.splitlines()]


def leading_space_counts(text: str) -> list[int]:
    return [len(line) - len(line.lstrip(" ")) for line in text.splitlines()]


_SHAPE_KEY_FIELDS = (
    ("Surface", "surface_mask", "# = defined terrain · . = outside crop"),
    ("Elevation", "elevation_map", "1 = upper plane · 0 = lower plane"),
    ("Walkable", "walkable_mask", "# = walkable lower plane · . = not walkable"),
    ("Mask", "mask", "# = included cell · . = excluded cell"),
)


def shape_key(sample: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the logical masks and symbol meanings needed to read artwork."""

    sections: list[dict[str, Any]] = []
    for label, field, legend in _SHAPE_KEY_FIELDS:
        rows = sample.get(field)
        if isinstance(rows, list) and all(isinstance(row, str) for row in rows):
            sections.append({"label": label, "rows": rows, "legend": legend})
    return sections


@dataclass(frozen=True)
class Candidate:
    text: str
    source: str
    sha256: str


class ReviewState:
    def __init__(self, root: Path, *, enable_git_publish: bool = False) -> None:
        self.root = root.resolve()
        self.enable_git_publish = enable_git_publish
        self._lock = threading.RLock()

    @property
    def catalog_path(self) -> Path:
        return safe_project_path(self.root, CATALOG_PATH)

    def load_catalog(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise NotFoundError(f"Missing catalog: {CATALOG_PATH}") from exc
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Invalid catalog JSON: {exc}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("samples"), list):
            raise ValidationError("catalog_v2.json must contain a samples array.")
        return payload

    def sample_map(self) -> dict[str, dict[str, Any]]:
        mapping: dict[str, dict[str, Any]] = {}
        for sample in self.load_catalog()["samples"]:
            if not isinstance(sample, dict) or not isinstance(sample.get("id"), str):
                continue
            mapping[sample["id"]] = sample
        return mapping

    def get_sample(self, sample_id: str) -> dict[str, Any]:
        validate_sample_id(sample_id)
        sample = self.sample_map().get(sample_id)
        if sample is None:
            raise NotFoundError(f"Unknown sample: {sample_id}")
        return sample

    def _read_relative(self, relative: str) -> str | None:
        path = safe_project_path(self.root, relative)
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def _target_source(self, sample: dict[str, Any]) -> tuple[str, str] | None:
        explicit = sample.get("target")
        candidates: list[str] = []
        if isinstance(explicit, str):
            candidates.append(explicit)
        aliases = {
            "room-foreground-four-by-four-v2": "targets/room-foreground-walls-on.txt",
        }
        alias = aliases.get(str(sample.get("id", "")))
        if alias:
            candidates.append(alias)
        candidates.append(f"targets/{sample['id']}.txt")
        for relative in candidates:
            text = self._read_relative(
                f"style_samples/{relative}" if not relative.startswith("style_samples/") else relative
            )
            if text is not None:
                return text, relative
        return None

    def _candidate_source(self, sample: dict[str, Any]) -> tuple[str, str] | None:
        status = str(sample.get("status", ""))
        ordered_fields: list[str]
        if "candidate" in sample:
            ordered_fields = ["candidate", "review", "target"]
        elif status == "approved":
            ordered_fields = ["target", "review"]
        else:
            ordered_fields = ["review", "target"]
        for field in ordered_fields:
            value = sample.get(field)
            if isinstance(value, str):
                text = self._read_relative(f"style_samples/{value}" if not value.startswith("style_samples/") else value)
                if text is not None:
                    return text, value
        sample_id = sample["id"]
        conventional = f"style_samples/review/{sample_id}.txt"
        text = self._read_relative(conventional)
        if text is not None:
            return text, conventional
        return None

    def candidate_for(self, sample: dict[str, Any]) -> Candidate:
        source = self._candidate_source(sample)
        if source is not None:
            raw, relative = source
            text = extract_artwork(raw)
            return Candidate(text=text, source=relative, sha256=sha256_text(text))

        topology_parts: list[str] = []
        for label, key in (
            ("SURFACE", "surface_mask"),
            ("ELEVATION", "elevation_map"),
            ("WALKABLE", "walkable_mask"),
            ("MASK", "mask"),
        ):
            rows = sample.get(key)
            if isinstance(rows, list) and all(isinstance(row, str) for row in rows):
                topology_parts.extend([label, *rows, ""])
        if topology_parts:
            text = "\n".join(topology_parts).rstrip() + "\n"
            return Candidate(text=text, source="catalog topology", sha256=sha256_text(text))
        text = ""
        return Candidate(text=text, source="unavailable", sha256=sha256_text(text))

    def _reference_for(self, sample: dict[str, Any], samples: dict[str, dict[str, Any]]) -> tuple[str, str]:
        explicit = sample.get("reference")
        if isinstance(explicit, str):
            raw = self._read_relative(f"style_samples/{explicit}" if not explicit.startswith("style_samples/") else explicit)
            if raw is not None:
                return extract_artwork(raw), explicit

        reference_id = sample.get("reference_id")
        if isinstance(reference_id, str) and reference_id in samples:
            ref_candidate = self.candidate_for(samples[reference_id])
            return ref_candidate.text, ref_candidate.source

        category = sample.get("category")
        if category != "elevation":
            target = self._target_source(sample)
            if target is not None:
                raw, relative = target
                return extract_artwork(raw), relative

        if category == "room":
            relative = "targets/room-foreground-walls-on.txt"
            raw = self._read_relative(f"style_samples/{relative}")
            if raw is not None:
                return extract_artwork(raw), relative

        if category == "elevation":
            authoritative = samples.get("sunken-terrain-reference-v2")
            if authoritative and authoritative.get("id") != sample.get("id"):
                ref_candidate = self.candidate_for(authoritative)
                return ref_candidate.text, ref_candidate.source
        return "", ""

    def _previous_for(self, sample: dict[str, Any]) -> tuple[str, str]:
        previous = sample.get("previous_review") or sample.get("rejected_review")
        if isinstance(previous, str):
            raw = self._read_relative(f"style_samples/{previous}" if not previous.startswith("style_samples/") else previous)
            if raw is not None:
                return extract_artwork(raw), previous
        return "", ""

    def decision_path(self, sample_id: str) -> Path:
        return safe_project_path(self.root, DECISIONS_DIR / f"{validate_sample_id(sample_id)}.json")

    def correction_path(self, sample_id: str) -> Path:
        return safe_project_path(self.root, CORRECTIONS_DIR / f"{validate_sample_id(sample_id)}.txt")

    def read_decision(self, sample_id: str) -> dict[str, Any] | None:
        path = self.decision_path(sample_id)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return {"decision": "invalid", "error": "Decision file is not valid JSON."}
        return value if isinstance(value, dict) else {"decision": "invalid"}

    def read_correction(self, sample_id: str) -> str | None:
        try:
            return self.correction_path(sample_id).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def list_samples(self) -> list[dict[str, Any]]:
        samples = self.sample_map()
        output: list[dict[str, Any]] = []
        for sample in samples.values():
            candidate = self.candidate_for(sample)
            decision = self.read_decision(sample["id"])
            decision_hash = decision.get("candidate_sha256") if isinstance(decision, dict) else None
            recorded_correction_hash = decision.get("correction_sha256") if isinstance(decision, dict) else None
            correction_stale = False
            if isinstance(recorded_correction_hash, str):
                current_correction = self.read_correction(sample["id"])
                correction_stale = (
                    current_correction is None
                    or sha256_text(current_correction) != recorded_correction_hash
                )
            output.append(
                {
                    "id": sample["id"],
                    "title": sample.get("title", sample["id"]),
                    "category": sample.get("category", "uncategorized"),
                    "status": sample.get("status", "unknown"),
                    "candidate_sha256": candidate.sha256,
                    "candidate_available": bool(candidate.text),
                    "decision": decision.get("decision") if isinstance(decision, dict) else None,
                    "decision_stale": bool(
                        (decision_hash and decision_hash != candidate.sha256) or correction_stale
                    ),
                    "reviewed_at": decision.get("reviewed_at") if isinstance(decision, dict) else None,
                }
            )
        output.sort(key=lambda item: (item["status"] != "reviewing", item["category"], item["title"].lower()))
        return output

    def _elevation_vocabulary(
        self,
        samples: dict[str, dict[str, Any]],
        composition_source_ids: list[str],
    ) -> list[dict[str, Any]]:
        source_order = {
            source_id: index for index, source_id in enumerate(composition_source_ids)
        }
        vocabulary: list[dict[str, Any]] = []
        for sample in samples.values():
            if sample.get("category") != "elevation":
                continue
            status = str(sample.get("status", ""))
            if status not in {"approved", "authoritative"}:
                continue
            candidate = self.candidate_for(sample)
            if not candidate.text:
                continue
            vocabulary.append(
                {
                    "id": sample["id"],
                    "title": sample.get("title", sample["id"]),
                    "status": status,
                    "artwork": candidate.text,
                    "source": candidate.source,
                    "row_lengths": row_lengths(candidate.text),
                    "leading_spaces": leading_space_counts(candidate.text),
                    "shape_key": shape_key(sample),
                    "composition_source": sample["id"] in composition_source_ids,
                }
            )
        vocabulary.sort(
            key=lambda item: (
                not item["composition_source"],
                source_order.get(item["id"], len(source_order)),
                item["status"] != "authoritative",
                item["title"].lower(),
            )
        )
        return vocabulary

    def sample_detail(self, sample_id: str) -> dict[str, Any]:
        samples = self.sample_map()
        sample = samples.get(validate_sample_id(sample_id))
        if sample is None:
            raise NotFoundError(f"Unknown sample: {sample_id}")
        raw_composition_source_ids = sample.get("composition_source_ids", [])
        composition_source_ids = (
            list(
                dict.fromkeys(
                    source_id
                    for source_id in raw_composition_source_ids
                    if isinstance(source_id, str)
                )
            )
            if isinstance(raw_composition_source_ids, list)
            else []
        )
        candidate = self.candidate_for(sample)
        reference_text, reference_source = self._reference_for(sample, samples)
        previous_text, previous_source = self._previous_for(sample)
        correction = self.read_correction(sample_id)
        decision = self.read_decision(sample_id)
        correction_sha256 = sha256_text(correction) if correction is not None else None
        if (
            correction is not None
            and isinstance(decision, dict)
            and decision.get("decision") == "approved"
            and decision.get("candidate_sha256") == candidate.sha256
            and decision.get("correction_sha256") == correction_sha256
        ):
            reference_text = correction
            reference_source = f"corrections/{sample_id}.txt"
        if candidate.source == "catalog topology" and reference_text:
            editable_output = reference_text
            editable_source = reference_source
        else:
            editable_output = candidate.text
            editable_source = candidate.source
        if correction is not None:
            display_output = correction
            display_source = f"corrections/{sample_id}.txt"
        else:
            display_output = editable_output
            display_source = editable_source
        return {
            "sample": sample,
            "shape_key": shape_key(sample),
            "composition_source_ids": composition_source_ids,
            "elevation_vocabulary": (
                self._elevation_vocabulary(samples, composition_source_ids)
                if sample.get("category") == "elevation"
                else []
            ),
            "candidate": candidate.text,
            "candidate_source": candidate.source,
            "candidate_sha256": candidate.sha256,
            "candidate_row_lengths": row_lengths(candidate.text),
            "candidate_leading_spaces": leading_space_counts(candidate.text),
            "reference": reference_text,
            "reference_source": reference_source,
            "editable_output": editable_output,
            "editable_source": editable_source,
            "editable_sha256": sha256_text(editable_output),
            "display_output": display_output,
            "display_source": display_source,
            "display_sha256": sha256_text(display_output),
            "display_row_lengths": row_lengths(display_output),
            "display_leading_spaces": leading_space_counts(display_output),
            "previous": previous_text,
            "previous_source": previous_source,
            "correction": correction,
            "correction_sha256": correction_sha256,
            "decision": decision,
        }

    def _verify_hash(self, sample_id: str, submitted_hash: Any) -> Candidate:
        if not isinstance(submitted_hash, str):
            raise ValidationError("candidate_sha256 is required.")
        candidate = self.candidate_for(self.get_sample(sample_id))
        if submitted_hash != candidate.sha256:
            raise StaleCandidateError(
                "Candidate changed after it was loaded. Refresh before saving a correction or decision."
            )
        return candidate

    def save_correction(self, sample_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            candidate = self._verify_hash(sample_id, payload.get("candidate_sha256"))
            text = payload.get("text")
            if not isinstance(text, str):
                raise ValidationError("Correction text must be a string.")
            if "\x00" in text:
                raise ValidationError("Correction text may not contain NUL characters.")
            if len(text.encode("utf-8")) > MAX_BODY_BYTES:
                raise ValidationError("Correction is too large.")
            path = self.correction_path(sample_id)
            atomic_write_text(path, text)
            return {
                "sample_id": sample_id,
                "candidate_sha256": candidate.sha256,
                "correction": path.relative_to(self.root).as_posix(),
                "correction_source": path.relative_to(self.root / "style_samples").as_posix(),
                "correction_sha256": sha256_text(text),
                "correction_row_lengths": row_lengths(text),
                "correction_leading_spaces": leading_space_counts(text),
                "saved_at": utc_now(),
            }

    def save_decision(self, sample_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            candidate = self._verify_hash(sample_id, payload.get("candidate_sha256"))
            decision = payload.get("decision")
            if decision not in VALID_DECISIONS:
                raise ValidationError(f"Decision must be one of: {', '.join(sorted(VALID_DECISIONS))}.")
            notes = payload.get("notes", "")
            if not isinstance(notes, str):
                raise ValidationError("Notes must be a string.")
            notes = notes.strip()
            correction_path = self.correction_path(sample_id)
            record: dict[str, Any] = {
                "schema_version": 1,
                "sample_id": sample_id,
                "candidate_sha256": candidate.sha256,
                "decision": decision,
                "notes": notes,
                "reviewed_at": utc_now(),
            }
            if correction_path.exists():
                record["correction"] = correction_path.relative_to(self.root / "style_samples").as_posix()
                record["correction_sha256"] = sha256_text(correction_path.read_text(encoding="utf-8"))
            path = self.decision_path(sample_id)
            atomic_write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
            return record

    def git_status(self) -> dict[str, Any]:
        if not self.enable_git_publish:
            return {"enabled": False}
        branch = self._git("branch", "--show-current").strip()
        changed = self._git(
            "status",
            "--porcelain",
            "--",
            DECISIONS_DIR.as_posix(),
            CORRECTIONS_DIR.as_posix(),
        ).splitlines()
        return {"enabled": True, "branch": branch, "changed": changed}

    def _git(self, *args: str, check: bool = True) -> str:
        try:
            completed = subprocess.run(
                ["git", "-C", str(self.root), *args],
                check=check,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            stderr = getattr(exc, "stderr", "") or ""
            raise PublishError(stderr.strip() or f"git {' '.join(args)} failed") from exc
        return completed.stdout

    def publish_batch(self) -> dict[str, Any]:
        if not self.enable_git_publish:
            raise PublishError("Git publishing is disabled. Restart with --enable-git-publish.")
        with self._lock:
            top_level = Path(self._git("rev-parse", "--show-toplevel").strip()).resolve()
            if top_level != self.root:
                raise PublishError("The review app root is not the git repository root.")
            branch = self._git("branch", "--show-current").strip()
            if not branch:
                raise PublishError("Cannot publish from a detached HEAD.")
            if branch in {"main", "master", "phase-2-layout-generation"}:
                raise PublishError(f"Refusing to publish review files directly from protected branch {branch!r}.")

            pre_staged = [
                line
                for line in self._git("diff", "--cached", "--name-only").splitlines()
                if line
                and not line.startswith(f"{DECISIONS_DIR.as_posix()}/")
                and not line.startswith(f"{CORRECTIONS_DIR.as_posix()}/")
            ]
            if pre_staged:
                raise PublishError(
                    "Unrelated files are already staged. Unstage them before publishing the review batch."
                )

            self._git("add", "--", DECISIONS_DIR.as_posix(), CORRECTIONS_DIR.as_posix())
            staged = self._git("diff", "--cached", "--name-only").splitlines()
            if not staged:
                return {"published": False, "branch": branch, "message": "No review changes to publish."}
            invalid = [
                path
                for path in staged
                if not path.startswith(f"{DECISIONS_DIR.as_posix()}/")
                and not path.startswith(f"{CORRECTIONS_DIR.as_posix()}/")
            ]
            if invalid:
                raise PublishError("Refusing to commit files outside decisions and corrections.")

            self._git("commit", "-m", "review: record style sample decisions")
            commit_sha = self._git("rev-parse", "HEAD").strip()
            try:
                self._git("push")
            except PublishError as exc:
                raise PublishError(
                    f"Review commit {commit_sha[:12]} was created locally, but push failed: {exc}"
                ) from exc
            return {"published": True, "branch": branch, "commit_sha": commit_sha}


class ReviewRequestHandler(BaseHTTPRequestHandler):
    server_version = "AsciiReview/1.0"

    @property
    def app(self) -> "ReviewHTTPServer":
        return self.server  # type: ignore[return-value]

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"[review-app] {self.address_string()} {fmt % args}\n")

    def _common_headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")

    def _send_bytes(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self._common_headers(content_type, len(data))
        if content_type.startswith("text/html"):
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline'; connect-src 'self'; "
                "img-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
            )
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            pass

    def _send_json(self, status: int, payload: Any) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(status, data, "application/json; charset=utf-8")

    def _error(self, status: int, message: str) -> None:
        self._send_json(status, {"error": message})

    def _check_host(self) -> bool:
        host_header = self.headers.get("Host", "")
        hostname = urlparse(f"//{host_header}").hostname
        if self.app.loopback_only and hostname not in {"127.0.0.1", "localhost", "::1"}:
            self._error(HTTPStatus.FORBIDDEN, "Invalid Host header.")
            return False
        return True

    def _check_origin_and_token(self) -> bool:
        origin = self.headers.get("Origin")
        host = self.headers.get("Host")
        if origin and host and origin not in {f"http://{host}", f"https://{host}"}:
            self._error(HTTPStatus.FORBIDDEN, "Cross-origin writes are not allowed.")
            return False
        if self.headers.get("X-Review-Token") != self.app.token:
            self._error(HTTPStatus.FORBIDDEN, "Missing or invalid review token.")
            return False
        return True

    def _json_body(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise ValidationError("Content-Type must be application/json.")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValidationError("Invalid Content-Length.") from exc
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValidationError("Request body is empty or too large.")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError("Request body must be valid UTF-8 JSON.") from exc
        if not isinstance(payload, dict):
            raise ValidationError("JSON body must be an object.")
        return payload

    def do_GET(self) -> None:  # noqa: N802
        if not self._check_host():
            return
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            if path in {"/", "/review_app.html"}:
                html_path = safe_project_path(self.app.state.root, HTML_PATH)
                data = html_path.read_bytes()
                self._send_bytes(HTTPStatus.OK, data, "text/html; charset=utf-8")
                return
            if path == "/review_grid_editor.js":
                module_path = safe_project_path(self.app.state.root, GRID_EDITOR_PATH)
                self._send_bytes(
                    HTTPStatus.OK,
                    module_path.read_bytes(),
                    "text/javascript; charset=utf-8",
                )
                return
            if path == "/api/config":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "token": self.app.token,
                        "publish_enabled": self.app.state.enable_git_publish,
                    },
                )
                return
            if path == "/api/samples":
                self._send_json(HTTPStatus.OK, {"samples": self.app.state.list_samples()})
                return
            if path == "/api/git-status":
                self._send_json(HTTPStatus.OK, self.app.state.git_status())
                return
            prefix = "/api/sample/"
            if path.startswith(prefix):
                sample_id = unquote(path[len(prefix) :])
                self._send_json(HTTPStatus.OK, self.app.state.sample_detail(sample_id))
                return
            self._error(HTTPStatus.NOT_FOUND, "Not found.")
        except FileNotFoundError:
            self._error(HTTPStatus.NOT_FOUND, "review_app.html was not found.")
        except NotFoundError as exc:
            self._error(HTTPStatus.NOT_FOUND, str(exc))
        except ValidationError as exc:
            self._error(HTTPStatus.BAD_REQUEST, str(exc))
        except ReviewError as exc:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def do_POST(self) -> None:  # noqa: N802
        if not self._check_host() or not self._check_origin_and_token():
            return
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            payload = self._json_body()
            correction_prefix = "/api/correction/"
            decision_prefix = "/api/decision/"
            if path.startswith(correction_prefix):
                sample_id = unquote(path[len(correction_prefix) :])
                self._send_json(HTTPStatus.OK, self.app.state.save_correction(sample_id, payload))
                return
            if path.startswith(decision_prefix):
                sample_id = unquote(path[len(decision_prefix) :])
                self._send_json(HTTPStatus.OK, self.app.state.save_decision(sample_id, payload))
                return
            if path == "/api/publish":
                self._send_json(HTTPStatus.OK, self.app.state.publish_batch())
                return
            self._error(HTTPStatus.NOT_FOUND, "Not found.")
        except StaleCandidateError as exc:
            self._error(HTTPStatus.CONFLICT, str(exc))
        except NotFoundError as exc:
            self._error(HTTPStatus.NOT_FOUND, str(exc))
        except (ValidationError, PublishError) as exc:
            self._error(HTTPStatus.BAD_REQUEST, str(exc))
        except ReviewError as exc:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


class ReviewHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: ReviewState) -> None:
        super().__init__(address, ReviewRequestHandler)
        self.state = state
        self.loopback_only = address[0] in {"127.0.0.1", "localhost", "::1"}
        self.token = secrets.token_urlsafe(32)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local ASCII style-sample review inbox.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--enable-git-publish",
        action="store_true",
        help="Enable a button that commits and pushes decisions/corrections only.",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="Allow binding to a non-loopback host. Not recommended.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.host not in {"127.0.0.1", "localhost", "::1"} and not args.allow_remote:
        print("Refusing non-loopback binding without --allow-remote.", file=sys.stderr)
        return 2
    state = ReviewState(args.root, enable_git_publish=args.enable_git_publish)
    server = ReviewHTTPServer((args.host, args.port), state)
    display_host = "127.0.0.1" if args.host in {"0.0.0.0", "::"} else args.host
    url = f"http://{display_host}:{server.server_address[1]}"
    print(f"Review inbox: {url}")
    print(f"Project root: {state.root}")
    if args.enable_git_publish:
        print("Git review-batch publishing: enabled")
    if not args.no_browser:
        threading.Timer(0.2, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping review inbox.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
