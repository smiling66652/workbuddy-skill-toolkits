#!/usr/bin/env node
/**
 * playwright-cli 本地封装（零安装）
 *
 * Playwright 1.63+ 自带 `cli` 子命令，等价于全局 `playwright-cli`。
 * 本工具箱的 node_modules 里已有 playwright，所以**不需要**
 *   npm install -g @playwright/cli
 * 也能用完整的浏览器自动化命令集。
 *
 * 用法（与官方 playwright-cli 命令一致）：
 *   node scripts/pw.mjs open https://example.com --browser=msedge
 *   node scripts/pw.mjs snapshot
 *   node scripts/pw.mjs click e6
 *   node scripts/pw.mjs eval "() => document.title"
 *   node scripts/pw.mjs close
 *
 * 其他：
 *   node scripts/pw.mjs --self-check      检查本地 playwright 是否可用
 *   node scripts/pw.mjs --raw snapshot     全局选项原样透传（--raw / --json）
 *   node scripts/pw.mjs -s=name open x.com 命名会话（-s= 放在子命令前）
 *   node scripts/pw.mjs recording-start    录制操作 → recording-stop 输出 Playwright 代码
 *
 * 为什么默认用 msedge：
 *   系统已装 Edge，无需 `playwright install` 下载浏览器。
 *   `--browser` 实测可选值：chrome / firefox / webkit / msedge（官方 --help 口径）。
 *   ⚠️ --browser 只有 open 接受（实测 1.63.0），本脚本已只在 open 时注入。
 */

import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = resolve(__dirname, '..');

const CANDIDATES = [
  join(SKILL_DIR, 'node_modules', 'playwright', 'cli.js'),
  join(SKILL_DIR, 'node_modules', 'playwright-core', 'cli.js'),
];

const cli = CANDIDATES.find((p) => existsSync(p));

if (!cli) {
  console.error(
    [
      '[pw] 未找到本地 playwright。',
      '',
      '本脚本依赖工具箱自带的 node_modules。修复：',
      `  cd "${SKILL_DIR.replace(/\\/g, '/')}"`,
      '  npm install',
      '',
      '（不要装 @playwright/mcp —— 那是 MCP 服务端，不是这个 CLI）',
    ].join('\n')
  );
  process.exit(2);
}

const args = process.argv.slice(2);

if (args[0] === '--self-check') {
  const r = spawnSync(process.execPath, [cli, '--version'], { encoding: 'utf8' });
  console.log(`[pw] cli.js  : ${cli}`);
  console.log(`[pw] version : ${(r.stdout || r.stderr || '').trim()}`);
  console.log('[pw] 提示     : 默认请加 --browser=msedge 复用系统 Edge，免下载浏览器');
  process.exit(r.status === 0 ? 0 : 1);
}

if (args.length === 0) {
  console.error('[pw] 缺少参数。例：node scripts/pw.mjs open https://example.com --browser=msedge');
  process.exit(2);
}

// 未显式指定浏览器时，默认走系统 Edge（免下载）
// ⚠️ 实测 playwright 1.63：`--browser` 只有 `open` 接受，加到其它子命令上会
// 报 "Unknown option: --browser"。所以只在 open 时注入。
// 子命令 = 第一个不以 '-' 开头的参数（这样 `-s=name open ...` 也能正确识别）。
const subIdx = args.findIndex((a) => !a.startsWith('-'));
const sub = subIdx >= 0 ? args[subIdx] : '';
const hasBrowserFlag = args.some((a) => a.startsWith('--browser'));
if (sub === 'open' && !hasBrowserFlag) {
  args.push('--browser=msedge');
}

// 关键：不要让子进程的 stdout 被管道继承后阻塞（参见浏览器自动化.md 的"假性挂起"）
const r = spawnSync(process.execPath, [cli, 'cli', ...args], {
  stdio: 'inherit',
  windowsHide: true,
});

process.exit(r.status === null ? 1 : r.status);
