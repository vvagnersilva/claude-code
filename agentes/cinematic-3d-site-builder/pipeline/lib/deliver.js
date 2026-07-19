// pipeline/lib/deliver.js — Stage 6: finalize + report the output location.
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, ensureDir, copyFile, ok, info, c } from './util.js';

export function deliver(siteDir, qc) {
  // mirror QC screenshots into the site folder so the deliverable is self-contained
  if (qc?.screenshots?.length) {
    const dst = ensureDir(path.join(siteDir, 'qc'));
    for (const sp of qc.screenshots) { if (fs.existsSync(sp)) copyFile(sp, path.join(dst, path.basename(sp))); }
  }
  const abs = path.resolve(siteDir);
  const files = listTree(abs);
  console.log(`\n${c.bold(c.green('■ DELIVERED'))}`);
  console.log(`  ${c.bold('site:')} ${abs}`);
  console.log(`  ${c.bold('open:')} node pipeline/lib/server.js "${path.relative(ROOT, abs)}" 4890  → http://127.0.0.1:4890`);
  console.log(`  ${c.bold('files:')} ${files.length} (${(dirSize(abs) / 1024).toFixed(0)} KB)`);
  const qcLabel = qc?.pass === true ? c.green('PASS') : qc?.pass === false ? c.red('FAIL') : c.yellow('SKIPPED');
  ok(`QC: ${qcLabel} · continuityΔ=${qc?.checks?.pixelDeltaFirstLast ?? 'n/a'}`);
  return { path: abs, files };
}

function listTree(dir, base = dir, acc = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) listTree(p, base, acc);
    else acc.push(path.relative(base, p));
  }
  return acc;
}
function dirSize(dir) {
  let n = 0;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    n += e.isDirectory() ? dirSize(p) : fs.statSync(p).size;
  }
  return n;
}
