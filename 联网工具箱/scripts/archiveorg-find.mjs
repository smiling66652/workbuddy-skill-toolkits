#!/usr/bin/env node
/**
 * archiveorg-find.mjs  (API 版，比 UI 版更快更稳)
 * 通过 archive.org 的 advancedsearch + metadata 接口定位含 PDF 的条目，
 * 直接拿 /download/ 直链触发下载。全程走浏览器代理，规避慢 UI 翻页。
 *
 *   "C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe" \
 *     archiveorg-find.mjs --isbn 9787040422979 --name "热工基础-第3版-张学学" \
 *     --download-dir "D:/桌面/电子书/_downloads"
 */
import { chromium } from 'playwright';
import { argv } from 'process';
import fs from 'fs';
import os from 'os';
import path from 'path';
import net from 'net';

function getArg(name, def) {
  const i = argv.indexOf('--' + name);
  return i >= 0 && i + 1 < argv.length ? argv[i + 1] : def;
}
const isbn = (getArg('isbn') || '').replace(/[^0-9Xx]/g, '');
const query = getArg('query') || (isbn ? `ISBN:${isbn}` : '');
const name = getArg('name', isbn || 'book');
const downloadDir = getArg('download-dir', 'D:/桌面/电子书/_downloads');
const profile = getArg('profile', 'ArchiveAPI_' + Date.now());
const timeout = parseInt(getArg('timeout', '240000'), 10);

function probePort(port, host = '127.0.0.1') {
  return new Promise((r) => { const s = net.connect(port, host); s.setTimeout(800);
    s.once('connect', () => { s.destroy(); r(true); });
    s.once('error', () => { s.destroy(); r(false); });
    s.once('timeout', () => { s.destroy(); r(false); }); });
}
let proxyServer = getArg('proxy');
if (!proxyServer) {
  for (const [u, p] of [['http://127.0.0.1:10808', 10808], ['http://127.0.0.1:7890', 7890], ['http://127.0.0.1:10809', 10809]]) {
    if (await probePort(p)) { proxyServer = u; break; }
  }
}
console.log('[ia-find] proxy =', proxyServer || '(none)');
fs.mkdirSync(downloadDir, { recursive: true });

const localApp = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
const programFilesX86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';
const exe = path.join(programFilesX86, 'Microsoft', 'Edge', 'Application', 'msedge.exe');
if (!fs.existsSync(exe)) { console.error('[ia-find] 未找到 Edge'); process.exit(3); }
const userDataDir = path.join(localApp, 'Microsoft', 'Edge', 'User Data', profile);
console.log('[ia-find] edge =', exe, '| query =', query);

let finished = null;
const ctx = await chromium.launchPersistentContext(userDataDir, {
  headless: true, acceptDownloads: true,
  executablePath: exe, proxy: proxyServer ? { server: proxyServer } : undefined,
  args: ['--no-first-run', '--no-default-browser-check', '--disable-gpu'],
});
const page = ctx.pages()[0] || await ctx.newPage();
page.setDefaultTimeout(60000);
page.on('download', async (dl) => {
  const suggested = dl.suggestedFilename() || (name + '.pdf');
  const ext = path.extname(suggested) || '.pdf';
  const dest = path.join(downloadDir, name + ext);
  console.log('[ia-find] download event:', suggested);
  try { await dl.saveAs(dest); finished = dest; console.log('[ia-find] saved ->', dest); }
  catch (e) { console.error('[ia-find] save failed:', e.message); }
});
const log = (...a) => console.log('[ia-find]', ...a);
const deadline = Date.now() + timeout;

async function fetchJSON(url) {
  const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 50000 });
  const txt = await page.evaluate(() => document.body.innerText).catch(() => '');
  return JSON.parse(txt);
}

try {
  // 1) advancedsearch 拿 identifier 列表
  const q = isbn ? `ISBN:${isbn}` : query;
  const searchUrl = `https://archive.org/advancedsearch.php?q=${encodeURIComponent(q)}` +
    `+AND+mediatype%3Atexts&fl[]=identifier&fl[]=title&rows=15&page=1&output=json`;
  log('search ->', searchUrl);
  const data = await fetchJSON(searchUrl);
  const docs = (data && data.response && data.response.docs) || [];
  log('docs found:', docs.length);
  if (!docs.length) throw new Error('archive.org 无匹配条目');

  // 2) 逐个查 metadata，找 PDF
  for (const d of docs.slice(0, 8)) {
    if (Date.now() > deadline || finished) break;
    const id = d.identifier;
    log('check', id, d.title || '');
    try {
      const meta = await fetchJSON(`https://archive.org/metadata/${id}`);
      const files = (meta && meta.files) || [];
      // 优先选较大的 PDF（更像整本书）
      const pdfs = files.filter(f => /\.pdf$/i.test(f.name || '') && (f.size || 0) > 500000)
                        .sort((a, b) => (b.size || 0) - (a.size || 0));
      if (pdfs.length) {
        const f = pdfs[0];
        const dlUrl = `https://archive.org/download/${id}/${encodeURIComponent(f.name)}`;
        log('PDF found:', f.name, ((f.size || 0) / 1048576).toFixed(1) + 'MB', '->', dlUrl);
        await page.goto(dlUrl, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(e => log('goto warn:', e.message.split('\n')[0]));
        // 等待下载事件
        let waited = 0;
        while (!finished && waited < 120000) { await page.waitForTimeout(2000); waited += 2000; }
        if (finished) break;
      }
    } catch (e) { log('  meta err:', e.message.split('\n')[0]); }
  }
  if (!finished) throw new Error('未成功下载 PDF');
} catch (e) {
  console.error('[ia-find] 异常:', e.message);
} finally {
  await ctx.close();
}

if (finished && fs.existsSync(finished)) {
  console.log('[ia-find] SUCCESS', finished, '(' + (fs.statSync(finished).size / 1048576).toFixed(2) + ' MB)');
  process.exit(0);
} else {
  console.error('[ia-find] FAILED: 未获取到文件（' + name + '）');
  process.exit(4);
}
