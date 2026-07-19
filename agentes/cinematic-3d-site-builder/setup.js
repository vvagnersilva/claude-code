#!/usr/bin/env node
// setup.js — Assistente de configuração (pt-BR).
// Prepara tudo para o pipeline funcionar: dependências, browser do Playwright,
// ffmpeg, credenciais (.env) e um build de demonstração GRATUITO verificado.
//
//   npm run setup
//
// Zero dependências externas — roda com Node ≥ 18 puro.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline/promises';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const c = {
  bold: (s) => `\x1b[1m${s}\x1b[0m`,
  dim: (s) => `\x1b[2m${s}\x1b[0m`,
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  cyan: (s) => `\x1b[36m${s}\x1b[0m`,
};
const ok = (m) => console.log(`  ${c.green('✓')} ${m}`);
const info = (m) => console.log(`  ${c.dim('·')} ${m}`);
const warn = (m) => console.log(`  ${c.yellow('!')} ${m}`);
const fail = (m) => console.log(`  ${c.red('✗')} ${m}`);
const step = (n, t) => console.log(`\n${c.cyan(c.bold(`— Passo ${n} · ${t} `))}`);

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
// Robusto a stdin fechado (pipe, Ctrl+D, CI): a pergunta corre contra o evento
// 'close' e cai no valor padrão — `npm run setup < /dev/null` instala tudo com
// os defaults seguros (modo gratuito + demo).
let stdinFechado = false;
rl.on('close', () => { stdinFechado = true; });
const ask = async (q, padrao = '') => {
  if (stdinFechado) return padrao;
  try {
    const r = await Promise.race([
      rl.question(`  ${q}${padrao ? c.dim(` [${padrao}]`) : ''} `),
      new Promise((res) => rl.once('close', () => res(null))),
    ]);
    if (r === null) { console.log(''); return padrao; }
    return r.trim() || padrao;
  } catch { return padrao; }
};

async function main() {
  console.log(c.bold(c.cyan(`
╔════════════════════════════════════════════════════════════╗
║   CONSTRUTOR DE SITES 3D CINEMATOGRÁFICOS — CONFIGURAÇÃO    ║
║   brief → site com animação 3D real e scroll contínuo       ║
╚════════════════════════════════════════════════════════════╝`)));
  console.log(c.dim('  Este assistente prepara tudo e termina com um site de'));
  console.log(c.dim('  demonstração construído e verificado — sem gastar nada.'));

  // ── Passo 1 · Node ───────────────────────────────────────────────────────
  step(1, 'Verificando o Node.js');
  const major = parseInt(process.versions.node.split('.')[0], 10);
  if (major < 18) {
    fail(`Node ${process.versions.node} é antigo demais — este projeto exige Node ≥ 18.`);
    console.log('  Instale a versão LTS em https://nodejs.org e rode `npm run setup` de novo.');
    process.exit(1);
  }
  ok(`Node ${process.versions.node} — compatível.`);

  // ── Passo 2 · Dependências ───────────────────────────────────────────────
  step(2, 'Instalando dependências (npm install)');
  if (fs.existsSync(path.join(ROOT, 'node_modules', 'playwright'))) {
    ok('node_modules já presente — pulando.');
  } else {
    info('isso pode levar um minuto…');
    const r = spawnSync('npm', ['install'], { cwd: ROOT, stdio: 'inherit', shell: process.platform === 'win32' });
    if (r.status !== 0) { fail('npm install falhou — verifique sua conexão e tente de novo.'); process.exit(1); }
    ok('dependências instaladas.');
  }

  // ── Passo 3 · Browser do Playwright (etapa de verificação/QC) ────────────
  step(3, 'Instalando o Chromium do Playwright (QC automático)');
  const pw = spawnSync('npx', ['playwright', 'install', 'chromium'], { cwd: ROOT, stdio: 'inherit', shell: process.platform === 'win32' });
  if (pw.status !== 0) warn('não consegui instalar o Chromium — o build funciona, mas a etapa VERIFY será pulada (--no-verify).');
  else ok('Chromium pronto — o QC vai tirar screenshots e validar o 3D de verdade.');

  // ── Passo 4 · ffmpeg (opcional) ──────────────────────────────────────────
  step(4, 'Verificando o ffmpeg (opcional — só para clipes reais)');
  const ff = spawnSync('ffmpeg', ['-version'], { stdio: 'ignore', shell: process.platform === 'win32' });
  if (ff.status === 0) ok('ffmpeg encontrado — clipes reais serão decodificados em frames.');
  else {
    warn('ffmpeg não encontrado. Sem ele o modo frameseq com clipes REAIS não funciona.');
    info('macOS: brew install ffmpeg · Ubuntu/Debian: sudo apt install ffmpeg · Windows: winget install ffmpeg');
    info('Você pode instalar depois — o modo gratuito (stub) não precisa dele.');
  }

  // ── Passo 5 · Credenciais ────────────────────────────────────────────────
  step(5, 'Credenciais de geração (opcional)');
  console.log(`  O pipeline tem ${c.bold('dois modos')}:`);
  console.log(`  ${c.bold('GRATUITO (stub)')} — o site 3D completo com assets procedurais. Não precisa de chave.`);
  console.log(`  ${c.bold('REAL (fal.ai)')} — imagens e clipes de vídeo gerados por IA (Seedance 2.0 + Nano-Banana).`);
  console.log(`  ${c.dim('Crie uma chave em https://fal.ai/dashboard/keys (formato: id:segredo).')}`);
  console.log(`  ${c.dim('ATENÇÃO: geração real é PAGA (~US$ 10–30 por site completo). O gasto é medido e mostrado por build.')}`);
  let falKey = await ask('Cole sua FAL_KEY (Enter para pular e usar o modo gratuito):');
  if (falKey) {
    info('validando a chave na fal.ai…');
    try {
      const r = await fetch('https://rest.alpha.fal.ai/billing/user_balance', { headers: { Authorization: `Key ${falKey}` } });
      const body = (await r.text()).trim();
      const bal = parseFloat(body);
      if (r.ok && Number.isFinite(bal)) {
        ok(`chave válida — saldo atual: US$ ${bal.toFixed(2)}${bal <= 0 ? c.yellow(' (recarregue antes de um build real)') : ''}`);
      } else {
        warn(`a fal.ai não reconheceu a chave (resposta: ${body.slice(0, 80)}).`);
        const segue = await ask('Salvar mesmo assim? (s/N)', 'N');
        if (!/^s/i.test(segue)) falKey = '';
      }
    } catch { warn('não consegui falar com a fal.ai (sem internet?) — salvando sem validar.'); }
  } else {
    info('sem chave — o pipeline roda 100% no modo gratuito (stub).');
  }
  const hgKey = await ask('HIGGSFIELD_API_KEY, se você tiver uma (Enter para pular):');

  // grava o .env (nunca commitado — está no .gitignore)
  const envLines = [
    '# Credenciais — NUNCA commite este arquivo (já está no .gitignore).',
    '# Prioridade de provider: HIGGSFIELD_API_KEY > FAL_KEY > stub (gratuito).',
    '',
    ...(falKey ? [`FAL_KEY=${falKey}`] : ['# FAL_KEY=id:segredo            # crie em https://fal.ai/dashboard/keys']),
    ...(hgKey ? [`HIGGSFIELD_API_KEY=${hgKey}`] : ['# HIGGSFIELD_API_KEY=          # opcional']),
    '',
    '# Força assets gratuitos mesmo com chave configurada (iterar layout sem custo):',
    '# ASSETS_MODE=stub',
    '',
  ];
  fs.writeFileSync(path.join(ROOT, '.env'), envLines.join('\n'));
  ok(`.env gravado${falKey || hgKey ? '' : ' (modo gratuito)'} — edite quando quiser: ${c.dim('.env')}`);

  // ── Passo 6 · Build de demonstração (gratuito e verificado) ──────────────
  step(6, 'Build de demonstração (gratuito)');
  const roda = await ask('Construir o site-demonstração agora para validar tudo? (S/n)', 'S');
  if (/^s/i.test(roda)) {
    info('construindo briefs/example.brief.yaml em modo gratuito…');
    const args = ['pipeline/run.js', '--brief', 'briefs/example.brief.yaml'];
    if (pw.status !== 0) args.push('--no-verify');
    const demo = spawnSync('node', args, {
      cwd: ROOT, stdio: 'inherit',
      env: { ...process.env, ASSETS_MODE: 'stub' },
    });
    if (demo.status === 0) {
      console.log('');
      ok(c.bold('TUDO FUNCIONANDO! Seu primeiro site cinematográfico está pronto.'));
      info(`abra com:  ${c.bold('npm run serve -- output/abyssal 4890')}  →  http://127.0.0.1:4890`);
    } else {
      fail('o build de demonstração falhou — role para cima para ver o erro. Rode `npm run setup` de novo após corrigir.');
      process.exit(1);
    }
  } else {
    info('sem problema — rode depois:  ASSETS_MODE=stub npm run demo');
  }

  // ── Próximos passos ──────────────────────────────────────────────────────
  console.log(c.bold(c.cyan('\n╔══ PRÓXIMOS PASSOS ══╗')));
  console.log(`  ${c.bold('1.')} Site gratuito de qualquer ideia:   ${c.dim('ASSETS_MODE=stub npm run build -- --topic "uma cafeteria artesanal" --niche restaurant')}`);
  console.log(`  ${c.bold('2.')} Edite um brief pronto:             ${c.dim('briefs/*.brief.yaml (kaji, velluto, nocturne, eidolon, thock, volta)')}`);
  console.log(`  ${c.bold('3.')} Geração REAL (paga, com FAL_KEY):  ${c.dim('npm run build -- --brief briefs/nocturne.brief.yaml')}`);
  console.log(`  ${c.bold('4.')} Variante frame-scrubber (grátis):  ${c.dim('npm run build -- --brief <brief> --engine frameseq --out output/<slug>-frameseq --reuse-assets output/<slug>')}`);
  console.log(`  ${c.dim('Documentação: README.md · PIPELINE.md · briefs/schema.md')}\n`);
}

main().finally(() => rl.close());
