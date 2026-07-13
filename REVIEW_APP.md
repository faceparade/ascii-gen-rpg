# Local ASCII Review Inbox

Copy these files into the repository root.

## Run

Local-only decisions:

```bash
python review_app.py
```

To enable the **Publish review batch** button:

```bash
python review_app.py --enable-git-publish
```

Open `http://127.0.0.1:8765`.

## Review loop

1. Inspect generated and reference artwork.
2. Approve, reject, request changes, or skip.
3. Edit exact UTF-8 artwork and save a correction when needed.
4. Click **Publish review batch**.
5. Tell the assistant: `reviewed`.

The publish action stages, commits, and pushes only:

- `style_samples/decisions/`
- `style_samples/corrections/`

It refuses protected branches and refuses to run when unrelated files are already staged.

## Safety

Approving a candidate writes a decision file only. It never overwrites a golden target.
The decision records the candidate SHA-256, so stale approvals are rejected.

## Tests

```bash
pytest -q test_review_app.py
```
