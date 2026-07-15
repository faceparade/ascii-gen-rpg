import assert from "node:assert/strict";
import test from "node:test";

import {
  createDocument,
  deleteCell,
  deleteRow,
  eraseCell,
  History,
  insertCell,
  insertRow,
  paintCell,
  resizeRow,
  serializeDocument,
  shapeCellClass,
} from "./review_grid_editor.js";

test("text round-trips exact ragged rows, trailing spaces, and final newline", () => {
  const document = createDocument("  a  \n b\n");
  assert.deepEqual(document.rows, [[" ", " ", "a", " ", " "], [" ", "b"]]);
  assert.equal(document.finalNewline, true);
  assert.equal(serializeDocument(document), "  a  \n b\n");
});

test("painting an implicit cell extends only that row with explicit spaces", () => {
  const document = createDocument("a\nbb\n");
  paintCell(document, 0, 3, "|");
  assert.equal(serializeDocument(document), "a  |\nbb\n");
});

test("eraser writes an explicit space without silently shrinking the row", () => {
  const document = createDocument("abc\n");
  eraseCell(document, 0, 2);
  assert.equal(document.rows[0].length, 3);
  assert.equal(serializeDocument(document), "ab \n");
});

test("row-local cell insertion and deletion shift glyphs without counting spaces", () => {
  const document = createDocument("abc\n");
  insertCell(document, 0, 0);
  assert.equal(serializeDocument(document), " abc\n");
  deleteCell(document, 0, 0);
  assert.equal(serializeDocument(document), "abc\n");
});

test("row resize, insertion, and deletion preserve explicit dimensions", () => {
  const document = createDocument("ab\ncd\n");
  resizeRow(document, 0, 4);
  insertRow(document, 1, 3);
  assert.equal(serializeDocument(document), "ab  \n   \ncd\n");
  deleteRow(document, 1);
  resizeRow(document, 0, 1);
  assert.equal(serializeDocument(document), "a\ncd\n");
});

test("history records one snapshot per committed gesture", () => {
  const document = createDocument("ab\n");
  const history = new History(document);
  paintCell(document, 0, 0, "|");
  paintCell(document, 0, 1, "|");
  history.commit(document);
  assert.equal(serializeDocument(history.undo()), "ab\n");
  assert.equal(serializeDocument(history.redo()), "||\n");
});

test("topology cells distinguish elevated, lower, active, and blocked areas", () => {
  assert.equal(shapeCellClass("Elevation", "1"), "elevation-high");
  assert.equal(shapeCellClass("Elevation", "0"), "elevation-low");
  assert.equal(shapeCellClass("Surface", "1"), "mask-active");
  assert.equal(shapeCellClass("Surface", "#"), "mask-active");
  assert.equal(shapeCellClass("Walkable", "0"), "mask-inactive");
  assert.equal(shapeCellClass("Walkable", "."), "mask-inactive");
  assert.equal(shapeCellClass("Other", "x"), "mask-neutral");
});
