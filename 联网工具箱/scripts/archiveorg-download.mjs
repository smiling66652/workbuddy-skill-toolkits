#!/usr/bin/env node
/**
 * archiveorg-download.mjs
 * 通过 Internet Archive (archive.org) 按书名/ISBN 搜索并下载电子书 PDF。
 * archive.org 是合法公益数字图书馆，通常不在 VPN 服务商的盗版站屏蔽名单内，
 * 因此比 Anna's / Z-Library 更适合在受限代理下使用。
 *
 * 运行（managed node，脚本目录已自带 playwright）：
 *   "C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe" \
 *     archiveorg-download.mjs \
 *     --query "热工基础 张学学" \
 *     --isbn 9787040422979 \
 *     --name "热工基础-第3版-张学学" \
 *     --download-dir "D:/桌面/电子书/_downloads"
 *
 * 参数：
 *   --query         搜索关键词（书名/作者），可多个用空格分隔
 *   --isbn          可选，ISBN（优先用于精确匹配）
 *   --name          下载后文件名（不含扩展名）
 *   --download-dir  保存目录（默认 D:/桌面/电子书/_downloads）
 *   --browser       edge | chrome（默认 edge）
 *   --profile       独立浏览器档案名（默认 ArchiveBot）
 *   --headless      加此 flag 用无头模式
 *   --proxy         代理服务器（默认自动探测 127.0.0.1:10808）
 *   --timeout       单本总超时毫秒（默认 240000）
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

const query = getArg('query') || '';
const isbn = (getArg('isbn') || '').replace(/[^0-9Xx]/g, '');
const name = getArg('name', isbn || query || 'book');
const downloadDir = getArg('download-dir', 'D:/桌面/电子书/_downloads');
const requestedBrowser = getArg('browser', 'edge');
const profile = getArg('profile', 'ArchiveBot');
const headless = argv.includes('--headless');
const timeout = parseInt(getArg('timeout', '240000'), 10);

// ---- 自动探测本地 VPN 代理 ----
function probePort(port, host = '127.0.0.1') {
  return new Promise((resolve) => {
    const s = net.connect(port, host);
    s.setTimeout(800);
    s.once('connect', () => { s.destroy(); resolve(true); });
    s.once('error', () => { s.destroy(); resolve(false); });
    s.once('timeout', () => { s.destroy(); resolve(false); });
  });
}
const proxyArg = getArg('proxy');
let proxyServer = null;
if (proxyArg) {
  proxyServer = proxyArg;
} else {
  const candidates = [
    ['http://127.0.0.1:10808', 10808],
    ['http://127.0.0.1:7890', 7890],
    ['http://127.0.0.1:10809', 10809],
  ];
  for (const [url, port] of candidates) {
    if (await probePort(port)) { proxyServer = url; break; }
  }
}
console.log('[ia] proxy =', proxyServer || '(none, 直连)');

fs.mkdirSync(downloadDir, { recursive: true });

// ---- 浏览器探测（优先 Edge）----
const home = os.homedir();
const localApp = process.env.LOCALAPPDATA || path.join(home, 'AppData', 'Local');
const programFiles = process.env.PROGRAMFILES || 'C:\\Program Files';
const programFilesX86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';
const candidates = {
  edge: [
    path.join(programFilesX86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    path.join(programFiles, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    path.join(localApp, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
  ],
  chrome: [
    path.join(localApp, 'Google', 'Chrome', 'Application', 'chrome.exe'),
    path.join(programFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
  ],
};
let detected = null;
for (const b of ['edge', 'chrome']) {
  for (const exe of candidates[b]) {
    if (fs.existsSync(exe)) { detected = { b, exe }; break; }
  }
  if (detected) break;
}
if (!detected) { console.error('[ia] 未检测到 Edge/Chrome'); process.exit(3); }
const useBrowser = requestedBrowser === 'chrome' ? 'chrome' : detected.b;
const exe = detected.exe;
const userDataDir = path.join(localApp, useBrowser === 'edge' ? 'Microsoft' : 'Google',
  useBrowser === 'edge' ? 'Edge' : 'Chrome', 'User Data', profile);

console.log('[ia] browser =', useBrowser, exe);
console.log('[ia] query =', query, '| isbn =', isbn, '| name =', name);

let finished = null;
const launchOpts = {
  headless,
  acceptDownloads: true,
  args: ['--no-first-run', '--no-default-browser-check'],
  ...(useBrowser === 'edge' ? { executablePath: exe } : { channel: 'chrome' }),
};
if (proxyServer) launchOpts.proxy = { server: proxyServer };

const ctx = await chromium.launchPersistentContext(userDataDir, launchOpts);
const page = ctx.pages()[0] || await ctx.newPage();
page.setDefaultTimeout(60000);

page.on('download', async (dl) => {
  const suggested = dl.suggestedFilename() || (name + '.pdf');
  const ext = path.extname(suggested) || '.pdf';
  const dest = path.join(downloadDir, name + ext);
  console.log('[ia] download event:', suggested);
  try { await dl.saveAs(dest); finished = dest; console.log('[ia] saved ->', dest); }
  catch (e) { console.error('[ia] save failed:', e.message); }
});

const log = (...a) => console.log('[ia]', ...a);
const deadline = Date.now() + timeout;

// 构造搜索 URL：优先 ISBN，否则用关键词
const q = isbn ? `ISBN:${isbn}` : query;
const searchUrl = `https://archive.org/search?query=${encodeURIComponent(q)}&sin=${encodeURIComponent('')}&and[]=mediatype%3A%22texts%22`;
log('search ->', searchUrl);

let chosenItem = null;
try {
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('a[href^="/details/"]', { timeout: 30000 });

  // 收集前若干个条目链接
  const links = await page.locator('a[href^="/details/"]').evaluateAll(els =>
    Array.from(new Set(els.map(e => e.getAttribute('href')))).filter(h => /^\/details\//.test(h))
  );
  log('found', links.length, 'candidate items');

  // 逐个打开，找第一个带 PDF 下载的
  for (const href of links.slice(0, 6)) {
    if (Date.now() > deadline) break;
    const itemUrl = 'https://archive.org' + href;
    log('inspect ->', itemUrl);
    try {
      await page.goto(itemUrl, { waitUntil: 'domcontentloaded', timeout: 40000 });
    } catch (e) { log('  skip (timeout):', e.message.split('\n')[0]); continue; }

    // archive.org 的下载链接形如 /download/<id>/<file>.pdf 或 format:pdf 行
    const pdfLinks = await page.locator('a[href*="/download/"][href$=".pdf"]').evaluateAll(els => els.map(e => e.href));
    if (pdfLinks.length > 0) {
      chosenItem = { itemUrl, pdf: pdfLinks[0] };
      log('  PDF found:', pdfLinks[0]);
      break;
    }
    // 退一步：找 "PDF" 文本附近的链接
    const anyPdf = await page.locator('a:has-text("PDF")').first().getAttribute('href').catch(() => null);
    if (anyPdf) {
      chosenItem = { itemUrl, pdf: anyPdf.startsWith('http') ? anyPdf : 'https://archive.org' + anyPdf };
      log('  PDF(text) found:', chosenItem.pdf);
      break;
    }
  }

  if (!chosenItem) throw new Error('archive.org 未找到含 PDF 的匹配条目');

  // 触发下载
  log('downloading ->', chosenItem.pdf);
  const resp = await page.goto(chosenItem.pdf, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(e => { log('goto pdf err (maybe direct download):', e.message.split('\n')[0]); return null; });
  // 若 goto 未触发 download 事件（可能返回 HTML 页），尝试点击
  if (!finished) {
    const dlBtn = page.locator('a[href*="/download/"][href$=".pdf"]').first();
    if (await dlBtn.count() > 0) { await dlBtn.click(); }
  }
  // 等待下载落盘
  while (!finished && Date.now() < deadline) {
    await page.waitForTimeout(2000);
  }
} catch (e) {
  console.error('[ia] 流程异常:', e.message);
} finally {
  await ctx.close();
}

if (finished && fs.existsSync(finished)) {
  console.log('[ia] SUCCESS', finished, '(' + (fs.statSync(finished).size / 1024 / 1024).toFixed(2) + ' MB)');
  process.exit(0);
} else {
  console.error('[ia] FAILED: 未获取到文件（' + name + '）');
  process.exit(4);
}
