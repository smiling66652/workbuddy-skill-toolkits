#!/usr/bin/env node
/**
 * archiveorg-search-download.mjs
 * 1) 用 archive.org 网页搜索（已验证可用，返回 79 条候选）拿到真实书目 identifier；
 * 2) 用 page.evaluate(fetch) 调 /metadata 接口（走浏览器代理）精准筛出含 PDF 的条目；
 * 3) 直链 /download/ 触发下载。
 * 规避：advancedsearch 的 ISBN 字段索引坑 + UI 版把 /details/texts 当条目的坑。
 *
 *   "C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe" \
 *     archiveorg-search-download.mjs --isbn 9787040422979 --name "热工基础-第3版-张学学" \
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
const profile = getArg('profile', 'ArchiveSRCH_' + Date.now());
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
console.log('[ia-sd] proxy =', proxyServer || '(none)');
fs.mkdirSync(downloadDir, { recursive: true });

const localApp = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
const programFilesX86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';
const exe = path.join(programFilesX86, 'Microsoft', 'Edge', 'Application', 'msedge.exe');
if (!fs.existsSync(exe)) { console.error('[ia-sd] 未找到 Edge'); process.exit(3); }
const userDataDir = path.join(localApp, 'Microsoft', 'Edge', 'User Data', profile);
console.log('[ia-sd] edge =', exe, '| query =', query);

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
  console.log('[ia-sd] download event:', suggested);
  try { await dl.saveAs(dest); finished = dest; console.log('[ia-sd] saved ->', dest); }
  catch (e) { console.error('[ia-sd] save failed:', e.message); }
});
const log = (...a) => console.log('[ia-sd]', ...a);
const deadline = Date.now() + timeout;

try {
  // 1) 网页搜索
  const searchUrl = `https://archive.org/search?query=${encodeURIComponent(query)}`;
  log('search ->', searchUrl);
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('a[href^="/details/"]', { timeout: 30000 });

  // 2) 提取真实 identifier（排除 /details/texts、/details/about 等导航页）
  const ids = await page.evaluate(() => {
    const set = new Set();
    document.querySelectorAll('a[href^="/details/"]').forEach(a => {
      const h = (a.getAttribute('href') || '').split('?')[0];
      const m = h.match(/^\/details\/([^/]+)$/);
      if (m && !/^(texts|about|help|search)$/.test(m[1])) set.add(m[1]);
    });
    return [...set];
  });
  log('candidate identifiers:', ids.length, ids.slice(0, 12));
  if (!ids.length) throw new Error('未提取到书目 identifier');

  // 3) 逐个查 metadata，找 PDF
  for (const id of ids.slice(0, 12)) {
    if (Date.now() > deadline || finished) break;
    try {
      const meta = await page.evaluate(async (i) => {
        const r = await fetch(`https://archive.org/metadata/${i}`);
        return r.json();
      }, id);
      const files = (meta && meta.files) || [];
      const pdfs = files
        .filter(f => /\.pdf$/i.test(f.name || '') && (f.size || 0) > 500000)
        .sort((a, b) => (b.size || 0) - (a.size || 0));
      if (pdfs.length) {
        const f = pdfs[0];
        const dlUrl = `https://archive.org/download/${id}/${encodeURIComponent(f.name)}`;
        log('PDF @', id, '|', f.name, '|', (f.size / 1048576).toFixed(1) + 'MB');
        await page.goto(dlUrl, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(e => log('  goto warn:', e.message.split('\n')[0]));
        let waited = 0;
        while (!finished && waited < 120000) { await page.waitForTimeout(2000); waited += 2000; }
        if (finished) break;
      }
    } catch (e) { log('  meta err', id, ':', e.message.split('\n')[0]); }
  }
  if (!finished) throw new Error('79 条候选中未找到可直接下载的 PDF');
} catch (e) {
  console.error('[ia-sd] 异常:', e.message);
} finally {
  await ctx.close();
}

if (finished && fs.existsSync(finished)) {
  console.log('[ia-sd] SUCCESS', finished, '(' + (fs.statSync(finished).size / 1048576).toFixed(2) + ' MB)');
  process.exit(0);
} else {
  console.error('[ia-sd] FAILED: 未获取到文件（' + name + '）');
  process.exit(4);
}
