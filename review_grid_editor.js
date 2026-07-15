function assertRow(document, row) {
  if (!Number.isInteger(row) || row < 0 || row >= document.rows.length) {
    throw new RangeError(`row ${row} is outside the document`);
  }
}

function assertColumn(column) {
  if (!Number.isInteger(column) || column < 0) {
    throw new RangeError(`column ${column} is invalid`);
  }
}

function assertGlyph(glyph) {
  if (typeof glyph !== "string" || [...glyph].length !== 1 || glyph === "\n" || glyph === "\r") {
    throw new TypeError("glyph must be exactly one non-newline Unicode character");
  }
}

export function cloneDocument(document) {
  return {
    rows: document.rows.map(row => [...row]),
    finalNewline: Boolean(document.finalNewline),
  };
}

export function createDocument(text) {
  if (typeof text !== "string") throw new TypeError("text must be a string");
  const finalNewline = text.endsWith("\n");
  const body = finalNewline ? text.slice(0, -1) : text;
  return {
    rows: body.split("\n").map(row => [...row]),
    finalNewline,
  };
}

export function serializeDocument(document) {
  const body = document.rows.map(row => row.join("")).join("\n");
  return body + (document.finalNewline ? "\n" : "");
}

export function shapeCellClass(label, value) {
  const normalized = String(label).trim().toLowerCase();
  if (normalized === "elevation") {
    if (value === "1") return "elevation-high";
    if (value === "0") return "elevation-low";
  }
  if (value === "1" || value === "#") return "mask-active";
  if (value === "0" || value === ".") return "mask-inactive";
  return "mask-neutral";
}

export function paintCell(document, row, column, glyph) {
  assertRow(document, row);
  assertColumn(column);
  assertGlyph(glyph);
  const cells = document.rows[row];
  while (cells.length <= column) cells.push(" ");
  cells[column] = glyph;
}

export function eraseCell(document, row, column) {
  paintCell(document, row, column, " ");
}

export function insertCell(document, row, column) {
  assertRow(document, row);
  assertColumn(column);
  const cells = document.rows[row];
  while (cells.length < column) cells.push(" ");
  cells.splice(column, 0, " ");
}

export function deleteCell(document, row, column) {
  assertRow(document, row);
  assertColumn(column);
  if (column < document.rows[row].length) document.rows[row].splice(column, 1);
}

export function resizeRow(document, row, width) {
  assertRow(document, row);
  if (!Number.isInteger(width) || width < 0) throw new RangeError("row width must be a non-negative integer");
  const cells = document.rows[row];
  if (cells.length > width) cells.length = width;
  while (cells.length < width) cells.push(" ");
}

export function insertRow(document, index, width = 0) {
  if (!Number.isInteger(index) || index < 0 || index > document.rows.length) {
    throw new RangeError(`row insertion index ${index} is invalid`);
  }
  if (!Number.isInteger(width) || width < 0) throw new RangeError("row width must be a non-negative integer");
  document.rows.splice(index, 0, Array(width).fill(" "));
}

export function deleteRow(document, index) {
  assertRow(document, index);
  if (document.rows.length === 1) {
    document.rows[0] = [];
  } else {
    document.rows.splice(index, 1);
  }
}

export class History {
  constructor(document) {
    this.snapshots = [cloneDocument(document)];
    this.index = 0;
  }

  commit(document) {
    const current = serializeDocument(this.snapshots[this.index]);
    const next = serializeDocument(document);
    if (current === next) return;
    this.snapshots.splice(this.index + 1);
    this.snapshots.push(cloneDocument(document));
    this.index = this.snapshots.length - 1;
  }

  canUndo() {
    return this.index > 0;
  }

  canRedo() {
    return this.index + 1 < this.snapshots.length;
  }

  undo() {
    if (this.canUndo()) this.index -= 1;
    return cloneDocument(this.snapshots[this.index]);
  }

  redo() {
    if (this.canRedo()) this.index += 1;
    return cloneDocument(this.snapshots[this.index]);
  }
}
