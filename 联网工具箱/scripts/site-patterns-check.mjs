#!/usr/bin/env node
/**
 * 站点经验体检（site-patterns-check.mjs）
 *
 * 背景：2026-09-12 起 web-access 技能已删除，站点经验不再有「上游镜像」，
 *       references/site-patterns/ 就是唯一数据源，所以原先的「差异同步」脚本
 *       已无对象，改造为本体检脚本，负责守住质量。
 *
 * 检查项：
 *   1. frontmatter 是否完整（domain / aliases / updated）
 *   2. domain 是否为合法域名形态（不含协议、路径）
 *   3. 域名是否重复、别名是否跨文件冲突
 *   4. updated 是否陈旧（默认 >180 天提示）、是否为未来日期
 *   5. 正文是否为空壳（只有 frontmatter，没有「平台特征/有效模式/已知陷阱」任一节）
 *
 * 用法：
 *   node scripts/site-patterns-check.mjs            # 人读报告
 *   node scripts/site-patterns-check.mjs --json     # 机器可读
 *   node scripts/site-patterns-check.mjs --days 90  # 自定义陈旧阈值
 *
 * 退出码：0 = 无问题（陈旧只算提示）；1 = 有错误；2 = 目录不存在
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const PATTERNS_DIR = path.join(ROOT, 'references', 'site-patterns');

const argv = process.argv.slice(2);
const AS_JSON = argv.includes('--json');
const daysIdx = argv.indexOf('--days');
const STALE_DAYS = daysIdx >= 0 ? Number(argv[daysIdx + 1]) || 180 : 180;

if (!fs.existsSync(PATTERNS_DIR)) {
  if (AS_JSON) console.log(JSON.stringify({ ok: false, error: 'site-patterns 目录不存在', dir: PATTERNS_DIR }, null, 2));
  else console.error(`✗ 目录不存在：${PATTERNS_DIR}`);
  process.exit(2);
}

const files = fs.readdirSync(PATTERNS_DIR).filter((f) => f.endsWith('.md'));

/** 解析 frontmatter（只处理文件开头的 --- 块，数组支持行内 [a, b] 与 - 列表两种写法） */
function parseFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return null;
  const body = m[1];
  const fm = {};
  const lines = body.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const kv = line.match(/^([A-Za-z_][\w-]*)\s*:\s*(.*)$/);
    if (!kv) continue;
    const key = kv[1];
    let val = kv[2].trim();
    if (val === '') {
      // 可能是多行列表
      const items = [];
      for (let j = i + 1; j < lines.length; j++) {
        const it = lines[j].match(/^\s*-\s+(.*)$/);
        if (!it) break;
        items.push(it[1].trim());
        i = j;
      }
      fm[key] = items.length ? items : '';
    } else if (val.startsWith('[') && val.endsWith(']')) {
      fm[key] = val.slice(1, -1).split(',').map((s) => s.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
    } else {
      fm[key] = val.replace(/^["']|["']$/g, '');
    }
  }
  return { fm, rest: text.slice(m[0].length) };
}

const entries = [];
const errors = [];
const warnings = [];

for (const file of files) {
  const full = path.join(PATTERNS_DIR, file);
  let raw = '';
  try { raw = fs.readFileSync(full, 'utf8'); } catch (e) {
    errors.push({ file, msg: `读取失败：${e.message}` });
    continue;
  }
  const parsed = parseFrontmatter(raw);
  if (!parsed) {
    errors.push({ file, msg: '缺少 frontmatter（文件开头需有 --- 包裹的 YAML 块）' });
    continue;
  }
  const { fm, rest } = parsed;
  const domain = String(fm.domain || '').trim();
  const aliases = Array.isArray(fm.aliases) ? fm.aliases : (fm.aliases ? [String(fm.aliases)] : []);
  const updated = String(fm.updated || '').trim();

  if (!domain) errors.push({ file, msg: 'frontmatter 缺 domain' });
  else if (/^https?:\/\//i.test(domain)) errors.push({ file, msg: `domain 不应含协议：${domain}` });
  else if (/[/?#]/.test(domain)) errors.push({ file, msg: `domain 不应含路径/参数：${domain}` });
  else if (domain.toLowerCase() !== domain) warnings.push({ file, msg: `domain 建议小写：${domain}` });

  if (!updated) {
    errors.push({ file, msg: 'frontmatter 缺 updated（格式 YYYY-MM-DD）' });
  } else if (!/^\d{4}-\d{2}-\d{2}$/.test(updated)) {
    errors.push({ file, msg: `updated 格式非 YYYY-MM-DD：${updated}` });
  } else {
    const t = Date.parse(`${updated}T00:00:00Z`);
    const now = Date.now();
    const ageDays = Math.floor((now - t) / 86400000);
    if (ageDays < 0) warnings.push({ file, msg: `updated 是未来日期：${updated}` });
    else if (ageDays > STALE_DAYS) warnings.push({ file, msg: `updated 已 ${ageDays} 天未复核（阈值 ${STALE_DAYS}）` });
  }

  const sections = ['平台特征', '有效模式', '已知陷阱'];
  const present = sections.filter((s) => new RegExp(`^##+\\s*${s}`, 'm').test(rest));
  if (present.length === 0) {
    warnings.push({ file, msg: '正文没有「平台特征/有效模式/已知陷阱」任一节，可能是空壳' });
  }

  entries.push({ file, domain, aliases, updated, sections: present });
}

// 重复检查：域名与别名
const byKey = new Map();
for (const e of entries) {
  const keys = [e.domain, ...e.aliases].filter(Boolean).map((s) => s.toLowerCase());
  for (const k of keys) {
    if (!byKey.has(k)) byKey.set(k, []);
    byKey.get(k).push(e.file);
  }
}
const dupes = [...byKey.entries()].filter(([, v]) => v.length > 1);

const report = {
  dir: PATTERNS_DIR,
  count: files.length,
  staleThresholdDays: STALE_DAYS,
  errors,
  warnings,
  duplicates: dupes.map(([key, fs_]) => ({ key, files: fs_ })),
  entries,
};

if (AS_JSON) {
  console.log(JSON.stringify(report, null, 2));
} else {
  console.log(`站点经验体检 · ${PATTERNS_DIR}`);
  console.log(`共 ${files.length} 个文件，陈旧阈值 ${STALE_DAYS} 天\n`);
  if (entries.length) {
    console.log('条目：');
    for (const e of entries) {
      const alias = e.aliases.length ? `（别名：${e.aliases.join(', ')}）` : '';
      const sec = e.sections.length ? e.sections.join('/') : '无标准小节';
      console.log(`  - ${e.file}  domain=${e.domain || '?'}  updated=${e.updated || '?'}  [${sec}]${alias}`);
    }
    console.log('');
  }
  if (dupes.length) {
    console.log(`✗ 域名/别名冲突 ${dupes.length} 处：`);
    for (const [key, fs_] of dupes) console.log(`  - ${key} → ${fs_.join(' , ')}`);
    console.log('');
  }
  if (errors.length) {
    console.log(`✗ 错误 ${errors.length} 处：`);
    for (const e of errors) console.log(`  - ${e.file}: ${e.msg}`);
    console.log('');
  }
  if (warnings.length) {
    console.log(`⚠ 提示 ${warnings.length} 处：`);
    for (const w of warnings) console.log(`  - ${w.file}: ${w.msg}`);
    console.log('');
  }
  if (!errors.length && !warnings.length && !dupes.length) console.log('✓ 全部通过');
}

process.exit(errors.length || dupes.length ? 1 : 0);
