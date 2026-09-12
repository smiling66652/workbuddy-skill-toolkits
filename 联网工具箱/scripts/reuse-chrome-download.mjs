#!/usr/bin/env node
/**
 * reuse-browser-download.mjs
 * 复用本机浏览器已登录态，自动化下载电子书 / 文档。
 *
 * 原理：用 Playwright 驱动你本机已安装的 Edge/Chrome，
 * 并把 userDataDir 指向本机浏览器的 User Data 目录（默认即 Default 档案），
 * 从而直接继承 知网 / CARSI / 图书馆 / 各类已登录站点的 Cookie，无需重新登录。
 *
 * 运行（managed node，脚本目录已自带 playwright）：
 *   "C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe" \
 *   reuse-browser-download.mjs --url "<目标URL>" --download-dir "D:/桌面/电子书/_downloads"
 *
 * 常用参数：
 *   --url           必填，目标页面
 *   --download-dir  下载保存目录（默认 ~/Downloads/ebooks）
 *   --click         可选，触发下载的按钮/链接 CSS 选择器，命中后自动点击
 *   --profile       可选，子档案名（如 WorkBuddy）；省略则复用本机 Default（需先关闭其他浏览器窗口）
 *   --browser       可选，edge | chrome（默认自动检测：优先 Edge）
 *   --headless      可选，加此 flag 用无头模式
 *   --wait          下载等待毫秒数（默认 8000）
 *
 * 注意：复用 Default 档案时，请先关闭所有浏览器窗口（避免 SingletonLock 冲突）。
 *       若不想关浏览器，用 --profile WorkBuddy 走独立档案（首次需手动登录一次，之后复用）。
 */
import { chromium } from 'playwright';
import { argv } from 'process';
import fs from 'fs';
import os from 'os';
import path from 'path';

function getArg(name, def) {
  const i = argv.indexOf('--' + name);
  return i >= 0 && i + 1 < argv.length ? argv[i + 1] : def;
}

function detectBrowsers() {
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
      path.join(programFilesX86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
    ],
  };

  for (const browser of ['edge', 'chrome']) {
    for (const exe of candidates[browser]) {
      if (fs.existsSync(exe)) {
        const userData = path.join(localApp, browser === 'edge' ? 'Microsoft' : 'Google', browser === 'edge' ? 'Edge' : 'Chrome', 'User Data');
        return { browser, exe, userData };
      }
    }
  }
  return null;
}

const url = getArg('url');
if (!url) {
  console.error('[error] 缺少必填参数 --url');
  process.exit(1);
}

const downloadDir = getArg('download-dir', path.join(os.homedir(), 'Downloads', 'ebooks'));
const clickSel = getArg('click');
const profile = getArg('profile');
const requestedBrowser = getArg('browser');
const headless = argv.includes('--headless');
const waitMs = parseInt(getArg('wait', '8000'), 10);

fs.mkdirSync(downloadDir, { recursive: true });

const detected = detectBrowsers();
const useBrowser = requestedBrowser || (detected?.browser) || 'chrome';

if (!detected) {
  console.error('[error] 未检测到 Edge 或 Chrome 安装。请确认浏览器已安装，或用 --browser 指定。');
  process.exit(3);
}

const { exe, userData: detectedUserData } = detected;
const userDataDir = profile ? path.join(detectedUserData, profile) : detectedUserData;

console.log('[reuse-browser] 浏览器    =', useBrowser, exe);
console.log('[reuse-browser] userDataDir =', userDataDir);
console.log('[reuse-browser] downloadDir =', downloadDir);

let context;
try {
  const launchOpts = {
    headless,
    acceptDownloads: true,
    args: ['--no-first-run', '--no-default-browser-check'],
  };
  if (useBrowser === 'edge') {
    launchOpts.executablePath = exe;
  } else {
    launchOpts.channel = 'chrome';
  }
  context = await chromium.launchPersistentContext(userDataDir, launchOpts);
} catch (e) {
  console.error('[error] 启动浏览器失败：', e.message);
  console.error('提示：若报错含 SingletonLock，请先关闭所有浏览器窗口，或改用 --profile WorkBuddy 独立档案。');
  process.exit(2);
}

const page = context.pages()[0] || await context.newPage();
const downloaded = [];

page.on('download', async (dl) => {
  const fname = dl.suggestedFilename() || `download-${Date.now()}`;
  const dest = path.join(downloadDir, fname);
  console.log('[download] 开始保存:', fname);
  try {
    await dl.saveAs(dest);
    downloaded.push(dest);
    console.log('[download] 完成:', dest);
  } catch (err) {
    console.error('[download] 失败:', err.message);
  }
});

console.log('[reuse-browser] 打开:', url);
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

if (clickSel) {
  try {
    await page.waitForSelector(clickSel, { timeout: 15000 });
    await page.click(clickSel);
    console.log('[reuse-browser] 已点击:', clickSel);
  } catch (e) {
    console.warn('[warn] 未找到/点击失败:', clickSel, '-', e.message);
  }
}

// 等待下载触发并完成
await page.waitForTimeout(waitMs);
// 兜底：再等一会，确保进行中的下载落盘
await page.waitForTimeout(2000);

console.log('[reuse-browser] 完成。已保存文件:');
for (const f of downloaded) console.log('  -', f);
if (downloaded.length === 0) console.log('  （未捕获到下载事件，可尝试加 --click 指定下载按钮，或增大 --wait）');

await context.close();
