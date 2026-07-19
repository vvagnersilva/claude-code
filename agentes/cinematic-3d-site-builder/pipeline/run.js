#!/usr/bin/env node
// pipeline/run.js — orchestrator: INTAKE → PLAN → ASSETS → BUILD → VERIFY → DELIVER
import fs from 'node:fs';
import path from 'node:path';
import { intake } from './lib/intake.js';
import { plan } from './lib/plan.js';
import { assets } from './lib/assets.js';
import { build } from './lib/build.js';
import { verify } from './lib/verify.js';
import { deliver } from './lib/deliver.js';
import { ROOT, ensureDir, stage, ok, warn, c } from './lib/util.js';

function parseArgs(argv) {
  const o = { engine: 'webgl', verify: true };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === '--brief') o.brief = next();
    else if (a === '--topic') o.topic = next();
    else if (a === '--niche') o.niche = next();
    else if (a === '--engine') o.engine = next();
    else if (a === '--out') o.out = next();
    else if (a === '--no-verify') o.verify = false;
    else if (a === '--reuse-assets') {
      o.reuseAssets = true;
      // Optional value: reuse another build's assets (e.g. build the frameseq
      // variant of a paid webgl run into a separate output dir).
      if (argv[i + 1] && !argv[i + 1].startsWith('--')) o.assetsFrom = next();
    }
    else if (a === '--open') o.open = true;
    else if (a === '-h' || a === '--help') o.help = true;
  }
  return o;
}

const HELP = `
${c.bold('Cinematic 3D-Scroll Website Builder')}
  Turns a brief into a finished cinematic website with real 3D animation and a
  scroll-driven continuity effect. Runs all six pipeline stages.

${c.bold('Usage')}
  node pipeline/run.js --brief briefs/example.brief.yaml
  node pipeline/run.js --topic "a wood-fire steakhouse" --niche restaurant
  node pipeline/run.js --brief briefs/watch.brief.json --engine frameseq

${c.bold('Flags')}
  --brief <file>     YAML/JSON brief
  --topic "<idea>"   synthesize a brief from one line
  --niche <name>     template: luxury-product|journey|portfolio|ecommerce|restaurant|
                     real-estate|automotive|saas|agency|fitness (+ aliases)
  --engine <e>       webgl (default, real 3D) | frameseq (PDF frame-scrubber)
  --out <dir>        output dir (default output/<slug>)
  --no-verify        skip the Playwright QC stage
  --reuse-assets [d] reuse existing assets instead of regenerating — from this
                     build's out dir, or copied from another build dir [d]
                     (paid runs: build both engines for one spend)
`;

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || (!opts.brief && !opts.topic)) { console.log(HELP); process.exit(opts.help ? 0 : 1); }

  console.log(c.bold(c.cyan('\n╔══ CINEMATIC 3D-SCROLL WEBSITE PIPELINE ══╗')));

  // 1 · INTAKE
  stage('INTAKE', 'brief → normalized spec');
  const { brief, template } = intake(opts);

  // 2 · PLAN
  stage('PLAN', 'brief → storyboard + continuity map');
  const storyboard = plan({ brief, template });

  const outDir = opts.out
    ? (path.isAbsolute(opts.out) ? opts.out : path.join(ROOT, opts.out))
    : path.join(ROOT, 'output', brief.slug);
  ensureDir(outDir);

  // 3 · ASSETS
  stage('ASSETS', 'Higgsfield/Seedance (stub-safe) → manifest + placeholders');
  // --reuse-assets [dir]: paid generations are expensive — reuse a previous
  // run's assets (same dir, or copied from another build's output dir) instead
  // of regenerating. Typical use: build webgl once, then the frameseq variant.
  if (opts.assetsFrom) {
    const srcDir = path.isAbsolute(opts.assetsFrom) ? opts.assetsFrom : path.join(ROOT, opts.assetsFrom);
    const srcAssets = path.join(srcDir, 'assets');
    if (path.resolve(srcDir) !== path.resolve(outDir) && fs.existsSync(path.join(srcAssets, 'manifest.json'))) {
      fs.cpSync(srcAssets, path.join(outDir, 'assets'), { recursive: true });
      ok(`assets copied from ${path.relative(ROOT, srcAssets)}`);
    } else if (!fs.existsSync(path.join(srcAssets, 'manifest.json'))) {
      warn(`--reuse-assets ${opts.assetsFrom}: no manifest there — falling back to ${path.relative(ROOT, outDir)}`);
    }
  }
  const manifestPath = path.join(outDir, 'assets', 'manifest.json');
  let manifest;
  if (opts.reuseAssets && fs.existsSync(manifestPath)) {
    manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    ok(`assets REUSED from ${path.relative(ROOT, manifestPath)} (provider=${manifest.activeProvider || 'unknown'}, stubbed=${manifest.stubbed})`);
  } else {
    if (opts.reuseAssets) warn('--reuse-assets: no existing manifest — generating fresh');
    manifest = await assets(storyboard, outDir);
  }

  // 4 · BUILD
  stage('BUILD', `assemble self-contained site (engine=${opts.engine})`);
  const built = build(storyboard, manifest, outDir, { engine: opts.engine });

  // 5 · VERIFY
  let qc = { pass: null, checks: {}, screenshots: [] };
  if (opts.verify) {
    stage('VERIFY', 'Playwright QC — live WebGL + continuity across scroll');
    try {
      qc = await verify(outDir, { slug: brief.slug });
    } catch (e) {
      warn(`verify skipped: ${e.message}`);
      qc = { pass: null, checks: { note: 'verify unavailable: ' + e.message }, screenshots: [] };
    }
  } else {
    warn('verify skipped (--no-verify)');
  }

  // 6 · DELIVER
  stage('DELIVER', 'finalize output + report path');
  const out = deliver(outDir, qc);

  console.log(c.bold(c.cyan('\n╚══ PIPELINE COMPLETE ══╝')));
  console.log(`  ${c.bold('DEMO SITE:')} ${out.path}`);
  if (qc.pass === false) { console.log(c.red('  QC did not fully pass — see qc-report.json')); process.exitCode = 2; }
  return out;
}

main().catch((e) => { console.error(c.red('\nPIPELINE ERROR: ' + (e.stack || e.message || e))); process.exit(1); });
