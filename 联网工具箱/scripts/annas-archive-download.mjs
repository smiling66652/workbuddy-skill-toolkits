#!/usr/bin/env node
/**
 * annas-archive-download.mjs
 * 通过 Anna's Archive（annas-archive.org）按 ISBN 精准下载电子书 PDF。
 *
 * 适用场景：
 *   - 你开了 VPN，Anna's Archive 在国内需代理才能访问。
 *   - 该站「Slow download」免登录、稳定，本脚本自动化走这条路。
 *
 * 运行（managed node，脚本目录已自带 playwright）：
 *   "C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe" \
 *     annas-archive-download.mjs \
 *     --isbn 9787565066580 \
 *     --name "工程材料及成形技术基础-第2版-郑红梅" \
 *     --download-dir "D:/桌面/电子书/_downloads"
 *
 * 参数：
 *   --isbn          必填，ISBN（可含连字符）
 *   --name          下载后文件名（不含扩展名）
 *   --download-dir  保存目录（默认 D:/桌面/电子书/_downloads）
 *   --browser       edge | chrome（默认 edge）
 *   --profile       独立浏览器档案名（默认 AnnaBot，免登录、不占用你的主浏览器）
 *   --headless      加此 flag 用无头模式
 *   --proxy         代理服务器（默认自动探测 v2rayN/clash 常见本地端口）
 *   --timeout       单本总超时毫秒（默认 120000）
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
if (!isbn) { console.error('[error] 缺少必填参数 --isbn'); process.exit(1); }

const name = getArg('name', isbn);
const downloadDir = getArg('download-dir', 'D:/桌面/电子书/_downloads');
const requestedBrowser = getArg('browser', 'edge');
const profile = getArg('profile', 'AnnaBot');
const headless = argv.includes('--headless');
const timeout = parseInt(getArg('timeout', '120000'), 10);

// ---- 自动探测本地 VPN 代理（v2rayN 10808 / Clash 7890 等）----
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
    ['http://127.0.0.1:10808', 10808], // v2rayN 混合端口
    ['http://127.0.0.1:7890', 7890],  // Clash
    ['http://127.0.0.1:10809', 10809], // v2rayN HTTP
    ['socks5://127.0.0.1:10808', 10808],
  ];
  for (const [url, port] of candidates) {
    if (await probePort(port)) { proxyServer = url; break; }
  }
}
console.log('[anna] proxy =', proxyServer || '(none, 直连)');

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
if (!detected) { console.error('[error] 未检测到 Edge/Chrome'); process.exit(3); }
const useBrowser = requestedBrowser === 'chrome' ? 'chrome' : detected.b;
const exe = detected.exe;
const userDataDir = path.join(localApp, useBrowser === 'edge' ? 'Microsoft' : 'Google',
  useBrowser === 'edge' ? 'Edge' : 'Chrome', 'User Data', profile);

console.log('[anna] browser =', useBrowser, exe);
console.log('[anna] userDataDir =', userDataDir);
console.log('[anna] ISBN =', isbn, '| name =', name);

const downloadFile = path.join(downloadDir, name + '.pdf');
let finished = null;

const launchOpts = {
  headless,
  acceptDownloads: true,
  args: ['--no-first-run', '--no-default-browser-check'],
  ...(useBrowser === 'edge' ? { executablePath: exe } : { channel: 'chrome' }),
};
if (proxyServer) {
  launchOpts.proxy = { server: proxyServer };
}
const ctx = await chromium.launchPersistentContext(userDataDir, launchOpts);

const page = ctx.pages()[0] || await ctx.newPage();
page.on('download', async (dl) => {
  const suggested = dl.suggestedFilename() || (name + '.pdf');
  const dest = path.join(downloadDir, name + path.extname(suggested) || '.pdf');
  console.log('[anna] download event:', suggested);
  try { await dl.saveAs(dest); finished = dest; console.log('[anna] saved ->', dest); }
  catch (e) { console.error('[anna] save failed:', e.message); }
});

const log = (...a) => console.log('[anna]', ...a);
const deadline = Date.now() + timeout;

try {
  // 1) 搜索
  const searchUrl = `https://annas-archive.org/search?q=${isbn}&ext=pdf`;
  log('search ->', searchUrl);
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 150000 });

  // 2) 等待结果，点第一个书目链接
  await page.waitForSelector('a[href^="/md5/"]', { timeout: 90000 });
  const firstBook = page.locator('a[href^="/md5/"]').first();
  const bookHref = await firstBook.getAttribute('href');
  log('first book ->', bookHref);
  await firstBook.click();
  await page.waitForLoadState('domcontentloaded', { timeout: 30000 });

  // 3) 找到下载区，优先 Slow download
  log('looking for download button...');
  let clicked = false;
  for (const label of ['Slow download', 'slow download']) {
    const loc = page.getByText(label, { exact: false });
    if (await loc.count() > 0) {
      await loc.first().click();
      clicked = true;
      log('clicked:', label);
      break;
    }
  }
  if (!clicked) {
    // 兜底：直接找含 /slow_download/ 或 /download/ 的链接
    const direct = page.locator('a[href*="/slow_download/"], a[href*="/download/"]').first();
    if (await direct.count() > 0) { await direct.click(); clicked = true; log('clicked direct dl link'); }
  }
  if (!clicked) throw new Error('未找到下载入口（可能该书无 PDF 或页面结构变化）');

  // 4) 处理慢速下载排队页：等待「Download file」链接出现并点击
  await page.waitForTimeout(3000);
  // Anna's 慢速页可能自动触发下载（download 事件已捕获），也可能出现「Download file」按钮
  const dlLocator = page.getByText('Download file', { exact: false });
  if (await dlLocator.count() > 0) {
    log('clicking "Download file"');
    await dlLocator.first().click();
  } else {
    // 尝试直接 download 链接
    const a = page.locator('a[href*="/download/"]').first();
    if (await a.count() > 0) { log('clicking /download/ link'); await a.first().click(); }
  }

  // 5) 等待下载落盘
  while (!finished && Date.now() < deadline) {
    await page.waitForTimeout(2000);
    // 若慢速页还有二次「Download file」
    const df = page.getByText('Download file', { exact: false });
    if (await df.count() > 0) { try { await df.first().click(); } catch {} }
  }
} catch (e) {
  console.error('[anna] 流程异常:', e.message);
} finally {
  await ctx.close();
}

if (finished && fs.existsSync(finished)) {
  console.log('[anna] SUCCESS', finished, '(' + (fs.statSync(finished).size / 1024 / 1024).toFixed(2) + ' MB)');
  process.exit(0);
} else {
  console.error('[anna] FAILED: 未获取到文件（' + name + ' / ISBN ' + isbn + '）');
  process.exit(4);
}
