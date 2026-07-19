#!/usr/bin/env node
// Injects the DATA object into the report template and writes the final HTML.
// Robust against templates that mention the marker strings outside the real
// script block (e.g. in HTML comments).
//
// Usage: node inject-data.js <template.html> <data.json> <out.html>

const fs = require('fs');

const [, , templatePath, dataPath, outPath] = process.argv;
if (!templatePath || !dataPath || !outPath) {
  console.error('Usage: inject-data.js <template> <data.json> <out.html>');
  process.exit(2);
}

const template = fs.readFileSync(templatePath, 'utf8');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

const scriptOpen = template.indexOf('<script>');
const scriptClose = template.indexOf('</script>', scriptOpen);
if (scriptOpen === -1 || scriptClose === -1) {
  console.error('FATAL: template has no <script> block');
  process.exit(1);
}

const startMarker = '/*__DATA_START__*/';
const endMarker = '/*__DATA_END__*/';
const startInScript = template.indexOf(startMarker, scriptOpen);
const endInScript = template.indexOf(endMarker, startInScript);
if (startInScript === -1 || endInScript === -1 || startInScript > scriptClose || endInScript > scriptClose) {
  console.error('FATAL: DATA markers not found inside the <script> block');
  process.exit(1);
}

const replacement =
  startMarker + '\nconst DATA = ' + JSON.stringify(data, null, 2) + ';\n' + endMarker;

const out =
  template.slice(0, startInScript) +
  replacement +
  template.slice(endInScript + endMarker.length);

if (/REPLACE_WITH_BASE64/.test(out)) {
  console.error('FATAL: placeholder REPLACE_WITH_BASE64 still present after injection');
  process.exit(1);
}
if ((out.match(/const DATA = /g) || []).length !== 1) {
  console.error('FATAL: expected exactly one "const DATA =" after injection');
  process.exit(1);
}

fs.writeFileSync(outPath, out);
const sizeMB = (out.length / 1024 / 1024).toFixed(2);
console.log(`Wrote ${outPath} (${sizeMB} MB, month=${data.month.length}, week=${data.week.length})`);
