// Minimal block renderer for the R2 documents (docx-js).
const d = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
        HeadingLevel, AlignmentType, LevelFormat, BorderStyle } = d;

function runs(text, base = {}) {
  // **bold** and ^^italic^^ markup
  const out = [];
  const re = /(\*\*[^*]+\*\*|\^\^[^^]+\^\^)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith('**')) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else out.push(new TextRun({ text: t.slice(2, -2), italics: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o.run || {}), spacing: { after: 120 }, ...o.para });
const H = (t, lvl) => new Paragraph({ heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1],
                                      children: [new TextRun(t)], spacing: { before: 240, after: 120 } });
const B = (t, level = 0) => new Paragraph({ numbering: { reference: 'bul', level }, children: runs(t), spacing: { after: 60 } });
const N = (t) => new Paragraph({ numbering: { reference: 'num', level: 0 }, children: runs(t), spacing: { after: 60 } });
const qruns = (t) => t.split('\n').flatMap((line, i) => i ? [new TextRun({ break: 1 }), ...runs(line)] : runs(line));
const Q = (t) => new Paragraph({ children: qruns(t), indent: { left: 567 }, spacing: { after: 120 },
                                 shading: { type: ShadingType.CLEAR, fill: 'EEF3F8', color: 'auto' },
                                 border: { left: { style: BorderStyle.SINGLE, size: 12, color: '2E5C8A', space: 6 } } });
function T(rows, widths, total = 9360) {
  const w = widths || rows[0].map(() => Math.floor(total / rows[0].length));
  const sum = w.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: sum, type: WidthType.DXA }, columnWidths: w,
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, children: r.map((c, j) => new TableCell({
      width: { size: w[j], type: WidthType.DXA },
      shading: i === 0 ? { type: ShadingType.CLEAR, fill: 'D9E2EC', color: 'auto' } : undefined,
      margins: { top: 40, bottom: 40, left: 80, right: 80 },
      children: [new Paragraph({ children: runs(String(c), { size: 17, bold: i === 0 }) })] })) }))
  });
}
function doc(children, title) {
  return new Document({
    title, creator: 'Claude Code',
    styles: { default: { document: { run: { font: 'Calibri', size: 21 } } } },
    numbering: { config: [
      { reference: 'bul', levels: [0, 1].map(l => ({ level: l, format: LevelFormat.BULLET, text: l ? '–' : '•',
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567 * (l + 1), hanging: 283 } } } })) },
      { reference: 'num', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] }] },
    sections: [{ properties: { page: { size: { width: 11906, height: 16838 },
                 margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children }]
  });
}
const save = (document, path) => Packer.toBuffer(document).then(b => require('fs').writeFileSync(path, b));
module.exports = { P, H, B, N, Q, T, doc, save };
