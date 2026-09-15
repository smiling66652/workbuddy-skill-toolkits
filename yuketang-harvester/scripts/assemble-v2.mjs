// v2 装配：每门课一份讲义（有文字就出文字，没文字就出页图索引与文件位置）
import fs from "node:fs";
import path from "node:path";

const OUT = "D:/桌面/浏览器/yuketang-research";
const DATA = path.join(OUT, "harvest");
const SL = path.join(DATA, "slides");
const COURSES = path.join(OUT, "courses");
const CW = path.join(OUT, "courseware");
fs.mkdirSync(COURSES, { recursive: true });

const idx = JSON.parse(fs.readFileSync(path.join(DATA, "index.json"), "utf8"));
const byPid = new Map();
for (const f of fs.readdirSync(SL).filter((x) => x.endsWith(".json"))) {
  try { const o = JSON.parse(fs.readFileSync(path.join(SL, f), "utf8")); byPid.set(String(o.pid), o); } catch (e) {}
}
const safe = (s) => String(s || "").replace(/[\\/:*?"<>|]/g, "_").trim().slice(0, 50) || "course";

const rows = [];
let tPages = 0, tChars = 0, iPages = 0;

for (const c of idx.courses) {
  const md = [], outline = [];
  let pages = 0, chars = 0, imgOnly = 0, textDecks = 0, imgDecks = 0, probs = 0;
  md.push("# " + c.course, "");
  md.push("| 项 | 值 |", "|---|---|", "| 课程 | " + c.course + " |", "| 班级 | " + c.className + " |",
    "| 教师 | " + c.teacher + " |", "| 课时数 | " + c.lessons.length + " |", "| classroom_id | `" + c.cid + "` |", "");
  md.push("---", "");

  for (const l of c.lessons) {
    const d = new Date(l.ts);
    const ds = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    md.push("## " + ds + " · " + l.title, "");
    for (const p of l.pres) {
      const g = byPid.get(String(p.pid));
      md.push("### " + (p.title || "(无标题)"), "");
      if (!g || g.mode === "fail") { md.push("*(未采到)*", ""); continue; }
      const s = g.slides || [];
      pages += s.length;
      // 兼容 v1 遗留文件（无 mode 字段）：有文字就按文字型处理
      const isText = g.mode === "text" || (!g.mode && s.some((x) => x.t && x.t.length));
      if (isText) {
        textDecks++;
        const ch = s.reduce((a, x) => a + x.t.join("").length, 0);
        chars += ch; tPages += s.length; tChars += ch;
        md.push("> **文字版** ｜ " + s.length + " 页 ｜ " + ch + " 字 ｜ `" + p.pid + "`", "");
        for (const x of s) {
          const first = (x.t[0] || "").replace(/\n+/g, " ").slice(0, 70);
          outline.push("  p" + x.i + " " + (first || "(纯图形页)"));
          if (!x.t.length) continue;
          md.push("**第 " + x.i + " 页**", "");
          for (const tt of x.t) md.push("- " + tt.replace(/\n/g, " / "));
          md.push("");
        }
      } else {
        imgDecks++; iPages += s.length;
        const dir = path.join(CW, safe(c.course) + "__" + c.cid, safe(g.title || p.pid));
        const np = s.filter((x) => x.problem).length; probs += np;
        md.push("> **页图版**（该课件在前端只有图片、无文字层）｜ " + s.length + " 页 ｜ 图片目录：`" + path.relative(OUT, dir).replace(/\\/g, "/") + "`" + (np ? " ｜ 含题目 " + np + " 页" : ""), "");
        outline.push("  [页图] " + (g.title || p.pid) + " — " + s.length + " 页");
        md.push("");
      }
    }
    md.push("---", "");
  }
  const fn = safe(c.course) + "__" + c.cid;
  fs.writeFileSync(path.join(COURSES, fn + "-讲义.md"), md.join("\n"), "utf8");
  fs.writeFileSync(path.join(COURSES, fn + "-大纲.txt"), c.course + "\n\n" + outline.join("\n") + "\n", "utf8");
  rows.push({ ...c, pages, chars, imgDecks, textDecks, probs, fn });
  console.log("[ok] " + c.course.padEnd(24) + " 页 " + String(pages).padStart(5) + " | 文字 " + String(chars).padStart(6) + " 字 | 文字课件 " + textDecks + " / 页图课件 " + imgDecks);
}

const L = [];
L.push("# 全课程课件采集总览", "");
L.push("> 采集时间：" + new Date().toISOString(), "> 来源：长江雨课堂（本机 CDP 直连，纯读取）", "");
L.push("| 指标 | 值 |", "|---|---|");
L.push("| 有课件的课程 | " + rows.length + " |");
L.push("| 幻灯片总页数 | " + (tPages + iPages) + " |");
L.push("| **可直接喂 AI 的文字** | **" + tChars + " 字 / " + tPages + " 页** |");
L.push("| 仅页图（旧学期，无文字层） | " + iPages + " 页 |");
L.push("");
L.push("## 各课程", "");
L.push("| 课程 | 教师 | 课时 | 页数 | 文字量 | 课件形态 | 讲义 |");
L.push("|---|---|---|---|---|---|---|");
for (const r of rows.sort((a, b) => b.chars - a.chars || b.pages - a.pages)) {
  L.push("| " + r.course + " | " + r.teacher + " | " + r.lessons.length + " | " + r.pages + " | " + r.chars + " 字 | " +
    (r.textDecks && r.imgDecks ? "文字 " + r.textDecks + " + 页图 " + r.imgDecks : r.textDecks ? "全部文字版" : "全部页图版") +
    " | `courses/" + r.fn + "-讲义.md` |");
}
L.push("");
L.push("## 怎么用", "");
L.push("1. 先看 `courses/<课程>-大纲.txt`（每页首句拼成的骨架，3 分钟看全貌）。");
L.push("2. 把 `courses/<课程>-讲义.md` 整份丢给 AI，要求按章节出考点提纲 / 出题自测。");
L.push("3. 页图版课程的图片在 `courseware/<课程>__<cid>/<课件名>/p###.jpg`，可直接翻看或喂给支持视觉的模型。");
fs.writeFileSync(path.join(OUT, "08-全课程课件采集总览.md"), L.join("\n"), "utf8");
console.log("\n总计: 课程 " + rows.length + " | 页 " + (tPages + iPages) + " | 文字 " + tChars + " 字");
