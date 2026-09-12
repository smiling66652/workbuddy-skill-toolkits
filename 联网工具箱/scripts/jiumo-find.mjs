#!/usr/bin/env node
/**
 * jiumo-find.mjs  (鸠摩搜书兜底，应对 archive.org 无果时)
 * jiumo.net 为 Cloudflare 403 拦爬虫，本脚本用伪造 UA + 反检测参数尝试穿透，
 * 搜索目标并解析结果页中的下载线索（直链 / 网盘）。属于「尽力而为」兜底源。
 *
 *   "C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe" \
 *     jiumo-find.mjs --query "热工基础 张学学" --name "热工基础-第3版-张学学" \
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
const query = getArg('query') || '';
const isbn = (getArg('isbn') || '').replace(/[^0-9Xx]/g, '');
const name = getArg('name', query || 'book');
const downloadDir = getArg('download-dir', 'D:/桌面/电子书/_downloads');
const profile = getArg('profile', 'Jiumo_' + Date.now());
const timeout = parseInt(getArg('timeout', '180000'), 10);

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
console.log('[jiumo] proxy =', proxyServer || '(none)');
fs.mkdirSync(downloadDir, { recursive: true });

const localApp = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
const programFilesX86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';
const exe = path.join(programFilesX86, 'Microsoft', 'Edge', 'Application', 'msedge.exe');
if (!fs.existsSync(exe)) { console.error('[jiumo] 未找到 Edge'); process.exit(3); }
const userDataDir = path.join(localApp, 'Microsoft', 'Edge', 'User Data', profile);

// 伪造 UA + 反自动化检测
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
let finished = null;
const ctx = await chromium.launchPersistentContext(userDataDir, {
  headless: true, acceptDownloads: true,
  executablePath: exe, proxy: proxyServer ? { server: proxyServer } : undefined,
  userAgent: UA,
  args: [
    '--no-first-run', '--no-default-browser-check', '--disable-gpu',
    '--disable-blink-features=AutomationControlled',
    '--disable-features=IsolateOrigins,site-per-process',
  ],
});
const page = ctx.pages()[0] || await ctx.newPage();
await page.setExtraHTTPHeaders({ 'Accept-Language': 'zh-CN,zh;q=0.9' });
page.setDefaultTimeout(45000);
page.on('download', async (dl) => {
  const suggested = dl.suggestedFilename() || (name + '.pdf');
  const ext = path.extname(suggested) || '.pdf';
  const dest = path.join(downloadDir, name + ext);
  console.log('[jiumo] download event:', suggested);
  try { await dl.saveAs(dest); finished = dest; console.log('[jiumo] saved ->', dest); }
  catch (e) { console.error('[jiumo] save failed:', e.message); }
});
const log = (...a) => console.log('[jiumo]', ...a);
const deadline = Date.now() + timeout;

try {
  const q = isbn ? `${isbn} ${query}`.trim() : query;
  const url = `https://jiumo.net/?s=${encodeURIComponent(q)}`;
  log('search ->', url);
  const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch(e => { log('goto:', e.message.split('\n')[0]); return null; });
  if (!r || r.status() === 403) {
    log('被 Cloudflare 403 拦截，尝试备用域名/重试');
    // 尝试 jiumo 镜像
    const mirrors = ['https://www.jiumo.com/?s=' + encodeURIComponent(q), 'https://jiumo.mobi/?s=' + encodeURIComponent(q)];
    let ok = false;
    for (const m of mirrors) {
      const rr = await page.goto(m, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch(() => null);
      if (rr && rr.status() !== 403) { ok = true; break; }
    }
    if (!ok) throw new Error('jiumo 全部 403，CF 穿透失败');
  }
  await page.waitForTimeout(3000);
  // 解析结果：含「下载」或 .pdf 的链接
  const links = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('a').forEach(a => {
      const t = a.textContent || '';
      const h = a.href || '';
      if (/下载|\.pdf|pan\.baidu|lanzou|ctfile|quark/i.test(t + h)) out.push({ t: t.trim().slice(0, 40), h });
    });
    return out.slice(0, 20);
  });
  log('候选下载线索:', links.length);
  links.forEach(l => log('  -', l.t, '|', l.h));

  // 尝试点击第一个看起来像正文的条目
  const firstEntry = page.locator('a').filter({ hasText: /热工基础|张学学/ }).first();
  if (await firstEntry.count() > 0) {
    log('点击疑似条目...');
    await firstEntry.click().catch(e => log('click warn:', e.message.split('\n')[0]));
    await page.waitForTimeout(3000);
    const dl = page.locator('a:has-text("下载"), a[href$=".pdf"]').first();
    if (await dl.count() > 0) { await dl.click().catch(() => {}); }
    let w = 0; while (!finished && w < 90000) { await page.waitForTimeout(2000); w += 2000; }
  }
  if (!finished) throw new Error('jiumo 未直接落盘（多为网盘链接，需人工提取）');
} catch (e) {
  console.error('[jiumo] 异常:', e.message);
} finally {
  await ctx.close();
}

if (finished && fs.existsSync(finished)) {
  console.log('[jiumo] SUCCESS', finished, '(' + (fs.statSync(finished).size / 1048576).toFixed(2) + ' MB)');
  process.exit(0);
} else {
  console.error('[jiumo] FAILED: 未直接下载（' + name + '）');
  process.exit(4);
}
