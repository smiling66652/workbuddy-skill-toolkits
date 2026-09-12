#!/usr/bin/env node
/**
 * 联网工具箱 · 环境自检 (doctor)
 *
 * 目的：实测每一层「是不是真的能用」，输出能力矩阵。
 * SKILL.md 的层级推荐顺序应以此脚本的实测结果为准，而不是硬编码 P0/P1/P2。
 *
 * 用法：
 *   node scripts/doctor.mjs            # 人读表格
 *   node scripts/doctor.mjs --json     # 机器可读（Agent 用来动态决定路由）
 *   node scripts/doctor.mjs --quick    # 跳过联网探测（离线/省时）
 *   node scripts/doctor.mjs --no-net   # 同 --quick
 *
 * 退出码：0 = 至少 L1 可用；1 = 只剩静态层；2 = 环境本身有问题（Node/PATH）
 *
 * ⚠️ 已知坑：agent-browser 冷启动时 daemon 会继承 stdout，
 *    若把本脚本或 agent-browser 的输出接进管道（| head 等）会假性挂起。
 *    本脚本内部一律不用管道，输出也请重定向到文件而非接 head。
 */

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = resolve(__dirname, '..');
const SKILLS_ROOT = resolve(SKILL_DIR, '..');

const argv = process.argv.slice(2);
const AS_JSON = argv.includes('--json');
const QUICK = argv.includes('--quick') || argv.includes('--no-net');

const IS_WIN = process.platform === 'win32';
const results = [];

function record(layer, name, status, detail, fix) {
  results.push({ layer, name, status, detail: detail || '', fix: fix || '' });
}

/* ---------- 基础：Node 运行时 ---------- */

function checkNode() {
  const v = process.versions.node;
  const major = Number(v.split('.')[0]);
  // SKILL.md 要求 Node 22+（CDP Proxy 用原生 WebSocket）
  const canExec = run(process.execPath, ['-e', "process.stdout.write('ok')"]).out === 'ok';
  if (!canExec) {
    record('基础', 'Node 可执行代码', 'fail', `当前 ${v} 但无法执行代码（SIGILL/崩溃？）`,
      '换用托管 Node：C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe');
  } else if (major < 22) {
    record('基础', 'Node 版本', 'warn', `${v}（需 22+ 才有原生 WebSocket）`,
      '切到托管 Node 22.22.2-2');
  } else {
    record('基础', 'Node 版本', 'ok', v);
  }
  record('基础', 'Node 路径', 'ok', process.execPath);
}

/* ---------- 进程执行封装（处处带超时，绝不挂死） ---------- */

function run(cmd, args, timeout = 8000, opts = {}) {
  const r = spawnSync(cmd, args, {
    encoding: 'utf8',
    timeout,
    // Windows 下 npm bin 是 .cmd，必须走 shell；但 shell 会拆散含换行的参数
    // （多行 python -c 脚本会被切碎 → 静默返回空 → 误报"缺失"）。
    // 所以 python.exe 这类真 exe 一律用 shell:false。
    shell: opts.noShell ? false : IS_WIN,
    windowsHide: true,
  });
  return {
    ok: !r.error && r.status === 0,
    out: String(r.stdout || '').trim(),
    err: String(r.error?.code || r.stderr || '').trim(),
    status: r.status,
  };
}

/** 探测一个 CLI：既要存在，也要真能执行 */
function probeCli(layer, bin, versionArgs, fix) {
  const r = run(bin, versionArgs);
  if (r.ok && r.out) {
    const first = r.out.split('\n')[0].trim().slice(0, 60);
    record(layer, bin, 'ok', first);
    return true;
  }
  if (r.err === 'ENOENT' || !r.out) {
    record(layer, bin, 'fail', '未安装或不在 PATH', fix);
    return false;
  }
  record(layer, bin, 'warn', `执行异常：${(r.err || r.out).slice(0, 80)}`, fix);
  return false;
}

/* ---------- L0 静态层 ---------- */

function checkL0() {
  record('L0 静态层', 'WebSearch / WebFetch', 'ok', '由 Agent 内置工具提供，无需安装');
  const curl = run('curl', ['--version']);
  if (curl.ok) {
    record('L0 静态层', 'curl', 'ok', curl.out.split('\n')[0].trim().slice(0, 60));
  } else {
    record('L0 静态层', 'curl', 'warn', '未找到', 'Windows 自带 curl 位于 C:/Windows/System32/curl.exe');
  }
  // 校园网 schannel 证书吊销检查会卡住 curl，这是本机已知事实
  record('L0 静态层', 'curl 须知', 'warn', '本机校园网需加 --ssl-no-revoke，否则报 CRYPT_E_NO_REVOCATION_CHECK');
}

/* ---------- L0.5 Jina ---------- */

async function checkJina() {
  if (QUICK) {
    record('L0.5 Jina', '连通性', 'na', '已用 --quick 跳过');
    return;
  }
  const t0 = Date.now();
  try {
    const res = await withTimeout(
      fetch('https://r.jina.ai/https://example.com', { headers: { 'User-Agent': 'doctor.mjs' } }),
      20000
    );
    const ms = Date.now() - t0;
    if (res.ok) {
      record('L0.5 Jina', '连通性', 'ok', `HTTP ${res.status}，${ms}ms`);
    } else {
      record('L0.5 Jina', '连通性', 'warn', `HTTP ${res.status}（可能限流）`);
    }
  } catch (e) {
    // 本机 2026-09-11 实测：直连与 --socks5-hostname 走代理均为 000，不可达
    record('L0.5 Jina', '连通性', 'fail',
      `不可达：${String(e.message).slice(0, 50)}（本机直连/代理均失败）`,
      '改用 WebFetch（Agent 内置）+ 本地正文提取（trafilatura），不要依赖 Jina');
  }
  record('L0.5 Jina', '硬限制', 'warn', '不执行 JavaScript —— React/Vue/Notion 等 CS 页面会返回残缺 Markdown');
}

function withTimeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, rej) => setTimeout(() => rej(new Error(`timeout ${ms}ms`)), ms)),
  ]);
}

/* ---------- L1 CDP 直连 ---------- */

async function checkCdp() {
  const checkDeps = join(SKILL_DIR, 'scripts', 'check-deps.mjs');
  const cfgPath = join(SKILL_DIR, 'config.env');
  let browser = '';
  if (existsSync(cfgPath)) {
    const m = readFileSync(cfgPath, 'utf8').match(/^\s*WEB_ACCESS_BROWSER\s*=\s*(\S+)/m);
    if (m) browser = m[1];
  }
  record('L1 CDP 直连', 'CDP Proxy 脚本',
    existsSync(checkDeps) ? 'ok' : 'fail',
    checkDeps,
    'scripts/check-deps.mjs 缺失，从本技能仓库重新拉取');

  record('L1 CDP 直连', '浏览器偏好', browser ? 'ok' : 'warn',
    browser ? `WEB_ACCESS_BROWSER=${browser}` : 'config.env 未设，首次会询问用户',
    '写入 联网工具箱/config.env 的 WEB_ACCESS_BROWSER=edge|chrome');

  if (QUICK) {
    record('L1 CDP 直连', 'Proxy :3456', 'na', '已用 --quick 跳过');
    return;
  }
  try {
    const res = await withTimeout(fetch('http://127.0.0.1:3456/targets'), 3000);
    if (res.ok) {
      const body = await res.text();
      let n = 0;
      try { n = (JSON.parse(body).targets || JSON.parse(body) || []).length; } catch { /* 非 JSON 也算通 */ }
      record('L1 CDP 直连', 'Proxy :3456', 'ok', `已就绪，${n} 个 tab`);
    } else {
      record('L1 CDP 直连', 'Proxy :3456', 'warn', `HTTP ${res.status}`);
    }
  } catch {
    record('L1 CDP 直连', 'Proxy :3456', 'warn', '未运行',
      `启动：node "${checkDeps.replace(/\\/g, '/')}"`);
  }
}

/* ---------- L2 独立浏览器 ---------- */

function checkL2() {
  // 【首选】本目录自带的 playwright（1.63+ 有 `cli` 子命令 ≈ 全局 playwright-cli）
  // 零安装路径：走系统 Edge，不用下载浏览器
  const pwCli = join(SKILL_DIR, 'node_modules', 'playwright', 'cli.js');
  if (existsSync(pwCli)) {
    const v = run(process.execPath, [pwCli, '--version'], 20000);
    const ver = (v.out || '').replace(/^Version\s*/, '').trim() || '?';
    record('L2 独立浏览器', 'scripts/pw.mjs（本地 playwright）', 'ok',
      `${ver} · 零安装，默认走系统 Edge`);
  } else {
    record('L2 独立浏览器', 'scripts/pw.mjs（本地 playwright）', 'fail',
      '本目录 node_modules 缺 playwright',
      `cd "${SKILL_DIR.replace(/\\/g, '/')}" && npm install`);
  }

  const abOk = probeCli('L2 独立浏览器', 'agent-browser', ['--version'],
    'npm install -g agent-browser && agent-browser install');
  if (abOk) {
    // 冷启动管道假挂起是高频踩坑点，显式提示
    record('L2 独立浏览器', 'agent-browser 须知', 'warn',
      '冷启动时勿接管道（| head），daemon 继承 stdout 会导致假性挂起；重定向到文件');
  }
  // 全局 playwright-cli 已是可选：本机 pw.mjs 覆盖同样命令集
  probeCli('L2 独立浏览器', 'playwright-cli（全局，可选）', ['--version'],
    '可选。已有 scripts/pw.mjs 就无需安装；确需全局版用 npm install -g @playwright/cli（不是 @playwright/mcp）');
  // human-browser-cli 在 npm 上是 404（正确包名是 human-browser）；未验证且付费，不推荐
  probeCli('L2 独立浏览器', 'human-browser', ['--version'],
    'npm 上 human-browser-cli 为 404（正确包名 human-browser）；未验证且付费，见 references/反爬对抗.md');
}

/* ---------- Python 抓取栈 ---------- */

function findPython() {
  const cands = [
    join(SKILLS_ROOT, '..', 'binaries', 'python', 'envs', 'default', 'Scripts', 'python.exe'),
    join(SKILLS_ROOT, '..', 'binaries', 'python', 'envs', 'default', 'bin', 'python'),
    'C:/Users/Matebook/.workbuddy/binaries/python/versions/3.13.12/python.exe',
  ].map((p) => resolve(p));
  for (const c of cands) if (existsSync(c)) return c;
  return null;
}

function checkPython() {
  const py = findPython();
  if (!py) {
    record('Python 抓取栈', '解释器', 'fail', '未找到托管 Python', '检查 .workbuddy/binaries/python');
    return;
  }
  const v = run(py, ['-V'], 20000, { noShell: true });
  record('Python 抓取栈', '解释器', v.ok ? 'ok' : 'warn',
    `${(v.out || v.err).slice(0, 60)} · ${py}`);

  // pip 健康度：本机踩过坑 —— site-packages/pip/ 被剥离成只剩 _internal/_vendor，
  // 表现为「No module named pip.__main__」，所有装包都失败但报错像网络超时。
  const pip = run(py, ['-m', 'pip', '-V'], 30000, { noShell: true });
  if (pip.ok && /pip\s+\d/.test(pip.out)) {
    record('Python 抓取栈', 'pip 可用', 'ok', pip.out.split('\n')[0].trim().slice(0, 48));
  } else {
    record('Python 抓取栈', 'pip 损坏', 'fail',
      'python -m pip 无法执行（site-packages/pip 被剥离？）',
      `备份 site-packages/pip 与 pip-*.dist-info 后跑："${py}" -m ensurepip --upgrade --default-pip`);
  }

  const pkgs = [
    ['requests', 'HTTP 请求'],
    ['bs4', 'HTML 解析'],
    ['trafilatura', '正文提取去样板'],
    ['curl_cffi', 'TLS 指纹伪装（反爬）'],
    ['nodriver', '免 WebDriver 反爬（需 Python ≤3.13）'],
    ['yt_dlp', '视频/音频/字幕'],
  ];
  const script = pkgs.map(([p]) => `try:\n import ${p}\n print("${p}="+getattr(__import__("${p}"),"__version__","?"))\nexcept Exception as e:\n print("${p}=MISSING:"+type(e).__name__)`
  ).join('\n');
  const r = run(py, ['-c', script], 40000, { noShell: true });
  const found = Object.fromEntries(r.out.split('\n').filter(Boolean).map((l) => l.split('=')));
  const broken = [];
  for (const [p, desc] of pkgs) {
    const val = found[p];
    if (val && val !== 'MISSING' && !val.startsWith('MISSING:')) {
      record('Python 抓取栈', p, 'ok', `${val} · ${desc}`);
    } else if (val && val.startsWith('MISSING:ModuleNotFound') && val !== 'MISSING') {
      // 目录在但子模块缺失 = 包被剥离（本机 2026-09-11 遇到过 lxml / dateutil）
      broken.push(p);
      record('Python 抓取栈', p, 'fail', `已安装但导入失败（包被剥离？）· ${desc}`,
        `rm -rf <site-packages>/${p} 后重装：pip install ${p.replace('_', '-')}`);
    } else {
      record('Python 抓取栈', p, 'warn', `缺失 · ${desc}`,
        `"${py}" -m pip install ${p.replace('_', '-')} -i https://pypi.tuna.tsinghua.edu.cn/simple`);
    }
  }
  if (broken.length) {
    record('Python 抓取栈', '修复提示', 'warn',
      '本机 site-packages 存在"包目录被剥离"现象；pip 卸不掉（无 RECORD），须先 rm -rf 再装');
  }
}

/* ---------- 站点经验目录结构 ---------- */

function checkSitePatterns() {
  const own = join(SKILL_DIR, 'references', 'site-patterns');
  if (!existsSync(own)) {
    record('站点经验', '经验目录', 'warn', 'references/site-patterns 不存在');
    return;
  }
  // 2026-09-12 起 web-access 已删除，站点经验无上游镜像，本目录即唯一数据源
  record('站点经验', '经验目录', 'ok', `references/site-patterns（${countMd(own)} 个）`);
  const checker = join(__dirname, 'site-patterns-check.mjs');
  record('站点经验', '体检脚本', existsSync(checker) ? 'ok' : 'warn',
    existsSync(checker) ? 'site-patterns-check.mjs' : '缺失',
    '从本技能仓库重新拉取 scripts/');
}

function countMd(dir) {
  try { return readdirSync(dir).filter((f) => f.endsWith('.md')).length; } catch { return 0; }
}

/* ---------- 输出 ---------- */

const ICON = { ok: '[OK]', warn: '[!!]', fail: '[XX]', na: '[--]' };

function printHuman() {
  const byLayer = new Map();
  for (const r of results) {
    if (!byLayer.has(r.layer)) byLayer.set(r.layer, []);
    byLayer.get(r.layer).push(r);
  }
  console.log('\n联网工具箱 · 环境自检\n' + '='.repeat(64));
  for (const [layer, rows] of byLayer) {
    console.log(`\n## ${layer}`);
    for (const r of rows) {
      console.log(`${ICON[r.status]} ${r.name}${r.detail ? '  —  ' + r.detail : ''}`);
      if (r.fix && r.status !== 'ok') console.log(`     修复：${r.fix}`);
    }
  }
  const ok = results.filter((r) => r.status === 'ok').length;
  const warn = results.filter((r) => r.status === 'warn').length;
  const fail = results.filter((r) => r.status === 'fail').length;
  console.log('\n' + '='.repeat(64));
  console.log(`汇总：${ok} 正常 / ${warn} 需注意 / ${fail} 不可用`);
  console.log('提示：本脚本的网络探测在沙箱内可能被拦截；若 Jina/Proxy 显示不可达但确有服务，');
  console.log('      请以非沙箱方式重跑，或直接按 SKILL.md 的降级链继续。\n');
}

async function main() {
  checkNode();
  checkL0();
  await checkJina();
  await checkCdp();
  checkL2();
  checkPython();
  checkSitePatterns();

  if (AS_JSON) {
    console.log(JSON.stringify({
      generatedAt: new Date().toISOString(),
      platform: process.platform,
      node: process.versions.node,
      quick: QUICK,
      results,
      summary: {
        ok: results.filter((r) => r.status === 'ok').length,
        warn: results.filter((r) => r.status === 'warn').length,
        fail: results.filter((r) => r.status === 'fail').length,
      },
    }, null, 2));
  } else {
    printHuman();
  }

  const l1Ok = results.some((r) => r.layer === 'L1 CDP 直连' && r.name === 'Proxy :3456' && r.status === 'ok');
  const fatal = results.some((r) => r.layer === '基础' && r.status === 'fail');
  process.exit(fatal ? 2 : l1Ok ? 0 : 1);
}

main();
