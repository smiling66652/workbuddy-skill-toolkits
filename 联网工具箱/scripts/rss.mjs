#!/usr/bin/env node
/**
 * rss.mjs —— 零依赖 RSS / Atom 读取器
 *
 * 为什么不用 feedparser：
 *   RSS/Atom 就是 XML，用原生 fetch + 正则解析足够；少一个依赖、少一处装不上。
 *   本机 feedparser 从未安装，而新闻源全部可用 —— 不装也能干活。
 *
 * 用法：
 *   node scripts/rss.mjs --preset news                新华网时政 + 人民网时政
 *   node scripts/rss.mjs --preset tech                36氪 + 少数派
 *   node scripts/rss.mjs --preset all --limit 5
 *   node scripts/rss.mjs --url <feed> [--url <feed>]  自定义源（可重复）
 *   node scripts/rss.mjs --list-presets               列出内置源
 *   node scripts/rss.mjs --preset tech --since 1d     只看最近 1 天
 *   node scripts/rss.mjs --preset all --json          机器可读
 *
 * 设计要点：
 *   - 显式把「HTTP 200 但 body 为 0 字节」判为失败。知乎 /rss 就是这种假活源，
 *     只看状态码会以为它正常。
 *   - 输出为 Markdown 列表，可直接喂给总结环节。
 */

/**
 * 内置源状态均为 2026-09-11 逐个实测（看的是「最新条目的日期」，不是 HTTP 状态码）。
 *
 * ⚠️ 曾经的坑：新华网时政 / 人民网时政 都能返回 200 且条数不少（300 / 100），
 *    但**内容是冻结的**——新华网条目干脆没有 pubDate 且内容是 2022 年的，
 *    人民网最新条目停在 2025-06-05。只看"能抓到多少条"会以为它们是活源。
 *    所以判断一个源是否可用，必须看最新条目的时间，而不是条数。
 */
const PRESETS = {
  news: [
    { name: '中国新闻网', url: 'https://www.chinanews.com.cn/rss/scroll-news.xml' },
    { name: '界面新闻', url: 'https://a.jiemian.com/index.php?m=article&a=rss' },
  ],
  tech: [
    { name: '36氪', url: 'https://www.36kr.com/feed' },
    { name: 'IT之家', url: 'https://www.ithome.com/rss/' },
    { name: '少数派', url: 'https://sspai.com/feed' },
  ],
  ai: [
    { name: '量子位', url: 'https://www.qbitai.com/feed' },
    { name: '爱范儿', url: 'https://www.ifanr.com/feed' },
  ],
  dev: [
    { name: 'Solidot', url: 'https://www.solidot.org/index.rss' },
    { name: '小众软件', url: 'https://www.appinn.com/feed/' },
  ],
};
PRESETS.all = [...PRESETS.news, ...PRESETS.tech, ...PRESETS.ai, ...PRESETS.dev];

/* ---------------- 参数 ---------------- */

const argv = process.argv.slice(2);
const flags = new Set(argv.filter((a) => a.startsWith('--') && !a.includes('=')));
const urls = [];
for (let i = 0; i < argv.length; i++) if (argv[i] === '--url' && argv[i + 1]) urls.push(argv[++i]);

function opt(name, def) {
  const i = argv.indexOf('--' + name);
  return i >= 0 && i + 1 < argv.length && !argv[i + 1].startsWith('--') ? argv[i + 1] : def;
}

const LIMIT = parseInt(opt('limit', '10'), 10);
const SINCE = opt('since', '');
const AS_JSON = flags.has('--json');
const VERBOSE = flags.has('--verbose');

if (flags.has('--list-presets')) {
  console.log('可用内置源（2026-09-11 逐个实测「最新条目日期」）：\n');
  for (const [k, list] of Object.entries(PRESETS)) {
    if (k === 'all') continue;
    console.log(`  --preset ${k}`);
    for (const f of list) console.log(`      ${f.name.padEnd(12)} ${f.url}`);
  }
  console.log('\n已知失效，勿再使用（都是「看起来能抓、实际没用」的假活源）：');
  console.log('      新华网时政   — 200 且 300 条，但无 pubDate、内容是 2022 年的（冻结）');
  console.log('      人民网时政   — 200 且 100 条，最新条目停在 2025-06-05（冻结）');
  console.log('      知乎 /rss    — HTTP 200 但 body 为 0 字节');
  console.log('      机器之心     — 200 但 0 条目');
  console.log('      澎湃新闻     — 200 但 0 条目');
  console.log('      BBC / rsshub — 直连不可达（000）');
  process.exit(0);
}

let feeds = [];
const preset = opt('preset', '');
if (preset) {
  if (!PRESETS[preset]) {
    console.error(`[rss] 未知预设：${preset}。可选：${Object.keys(PRESETS).join(' / ')}`);
    process.exit(2);
  }
  feeds = PRESETS[preset].map((f) => ({ ...f }));
}
for (const u of urls) feeds.push({ name: new URL(u).hostname, url: u });

if (!feeds.length) {
  console.error('[rss] 需要 --preset <news|tech|all> 或 --url <feed>。用 --list-presets 看内置源。');
  process.exit(2);
}

/* ---------------- 解析 ---------------- */

const decode = (s) =>
  s.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#0?39;|&apos;/g, "'")
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim();

function pick(block, tags) {
  for (const t of tags) {
    const m = block.match(new RegExp(`<${t}[^>]*>([\\s\\S]*?)</${t}>`, 'i'));
    if (m) return decode(m[1]);
  }
  return '';
}

function parseFeed(xml) {
  const isAtom = /<entry[\s>]/i.test(xml);
  const itemTag = isAtom ? 'entry' : 'item';
  const blocks = xml.match(new RegExp(`<${itemTag}[\\s>][\\s\\S]*?</${itemTag}>`, 'gi')) || [];
  return blocks.map((b) => {
    let link = pick(b, ['link']);
    if (!link) {
      const m = b.match(/<link[^>]*href=["']([^"']+)["']/i);
      if (m) link = m[1];
    }
    return {
      title: pick(b, ['title']),
      link,
      date: pick(b, ['pubDate', 'published', 'updated', 'dc:date']),
      summary: pick(b, ['description', 'summary', 'content']).slice(0, 200),
    };
  });
}

function parseDate(s) {
  if (!s) return null;
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? null : d;
}

function withinSince(item) {
  if (!SINCE) return true;
  const m = SINCE.match(/^(\d+)([dhm])$/);
  if (!m) return true;
  const ms = { d: 864e5, h: 36e5, m: 6e4 }[m[2]] * Number(m[1]);
  const d = parseDate(item.date);
  if (!d) return true; // 没有日期就别过滤掉
  return Date.now() - d.getTime() <= ms;
}

/* ---------------- 抓取 ---------------- */

async function fetchFeed(feed) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 25000);
  try {
    const res = await fetch(feed.url, {
      signal: ctrl.signal,
      redirect: 'follow',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        Accept: 'application/rss+xml, application/xml, text/xml, */*',
      },
    });
    const body = await res.text();
    // 关键：200 但空 body 是假活源，必须当失败
    if (!body || body.length < 200) {
      return { ...feed, ok: false, error: `HTTP ${res.status} 但内容为空（${body.length} 字节）— 假活源` };
    }
    if (!res.ok) return { ...feed, ok: false, error: `HTTP ${res.status}` };
    return { ...feed, ok: true, items: parseFeed(body) };
  } catch (e) {
    return { ...feed, ok: false, error: e.name === 'AbortError' ? '超时 25s' : String(e.message || e) };
  } finally {
    clearTimeout(timer);
  }
}

/* ---------------- 主流程 ---------------- */

const results = await Promise.all(feeds.map(fetchFeed));

if (AS_JSON) {
  console.log(JSON.stringify({
    fetchedAt: new Date().toISOString(),
    since: SINCE || null,
    feeds: results.map((r) => ({
      name: r.name, url: r.url, ok: r.ok, error: r.error || null,
      count: r.ok ? r.items.filter(withinSince).length : 0,
      items: r.ok ? r.items.filter(withinSince).slice(0, LIMIT) : [],
    })),
  }, null, 2));
  process.exit(results.every((r) => r.ok) ? 0 : 1);
}

console.log(`\nRSS 抓取 · ${new Date().toLocaleString('zh-CN')}${SINCE ? ` · 仅最近 ${SINCE}` : ''}\n`);
console.log('='.repeat(62));

let total = 0;
for (const r of results) {
  console.log(`\n## ${r.name}`);
  console.log(`   ${r.url}`);
  if (!r.ok) {
    console.log(`   [XX] ${r.error}`);
    continue;
  }
  const items = r.items.filter(withinSince);
  if (VERBOSE && !items.length) console.log('   （该源未解析出条目，可能不是标准 RSS）');

  // 新鲜度检查：条数多不代表源是活的（新华网 300 条但内容是 2022 年的）
  const dates = r.items.map((it) => parseDate(it.date)).filter(Boolean).sort((a, b) => b - a);
  if (!dates.length) {
    console.log('   [!!] 该源所有条目都没有可用日期，无法判断新鲜度 —— 谨慎使用');
  } else {
    const days = (Date.now() - dates[0].getTime()) / 864e5;
    if (days > 30) {
      console.log(`   [!!] 疑似冻结源：最新条目已是 ${Math.round(days)} 天前（${dates[0].toLocaleDateString('zh-CN')}）`);
    } else if (days > 3) {
      console.log(`   [!!] 更新不频繁：最新条目 ${Math.round(days)} 天前`);
    }
  }

  for (const it of items.slice(0, LIMIT)) {
    total++;
    const d = parseDate(it.date);
    const when = d ? d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '  时间未知';
    console.log(`   - [${when}] ${it.title || '(无标题)'}`);
    if (it.link) console.log(`     ${it.link}`);
  }
  console.log(`   （共 ${items.length} 条，显示 ${Math.min(items.length, LIMIT)} 条）`);
}

console.log('\n' + '='.repeat(62));
console.log(`合计 ${total} 条。下一步：把上面的标题/链接按需抓正文并总结（见 内容总结.md）。`);
console.log('注意：标题是线索不是事实，需要引用时务必打开原文核对。\n');

process.exit(results.every((r) => r.ok) ? 0 : 1);
