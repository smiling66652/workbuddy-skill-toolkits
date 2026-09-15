// 下载全部"页图型"课件的幻灯片图片
import fs from "node:fs";
import path from "node:path";
import https from "node:https";
import { URL } from "node:url";

const OUT = "D:/桌面/浏览器/yuketang-research";
const SL = path.join(OUT, "harvest", "slides");
const DEST = path.join(OUT, "courseware");
const only = process.argv[2] || "";
const CONC = 6;

const safe = (s) => String(s || "").replace(/[\\/:*?"<>|]/g, "_").trim().slice(0, 50) || "course";
const files = fs.readdirSync(SL).filter((f) => f.endsWith(".json"));
const decks = [];
for (const f of files) {
  try {
    const o = JSON.parse(fs.readFileSync(path.join(SL, f), "utf8"));
    if (o.mode !== "image") continue;
    if (only && !String(o.course).includes(only)) continue;
    decks.push(o);
  } catch (e) {}
}
const jobs = [];
for (const d of decks) {
  // 目录名带 pid，避免同名课件互相覆盖
  const dir = path.join(DEST, safe(d.course) + "__" + d.cid, safe(d.title || d.pid) + "__" + d.pid);
  for (const s of d.slides) {
    if (!s.cover) continue;
    jobs.push({ url: s.cover, file: path.join(dir, "p" + String(s.i).padStart(3, "0") + ".jpg") });
  }
}
console.log("[dl] 课件 " + decks.length + " 个 / 页图 " + jobs.length + " 张");

function get(u, redir = 0) {
  return new Promise((res, rej) => {
    const rq = https.get(new URL(u), { timeout: 30000, rejectUnauthorized: false }, (rs) => {
      if ([301, 302, 307, 308].includes(rs.statusCode) && rs.headers.location && redir < 4) { rs.resume(); return get(rs.headers.location, redir + 1).then(res, rej); }
      const ch = []; rs.on("data", (c) => ch.push(c)); rs.on("end", () => res({ code: rs.statusCode, buf: Buffer.concat(ch) }));
    });
    rq.on("timeout", () => { rq.destroy(); rej(new Error("timeout")); });
    rq.on("error", rej);
  });
}

let idx = 0, ok = 0, bad = 0, skip = 0;
async function worker() {
  while (idx < jobs.length) {
    const my = idx++;
    const j = jobs[my];
    if (fs.existsSync(j.file) && fs.statSync(j.file).size > 3000) { skip++; continue; }
    try {
      fs.mkdirSync(path.dirname(j.file), { recursive: true });
      const r = await get(j.url);
      if (r.code === 200 && r.buf.length > 2000) { fs.writeFileSync(j.file, r.buf); ok++; }
      else bad++;
    } catch (e) { bad++; }
    if ((ok + skip + bad) % 100 === 0) console.log("  进度 " + (ok + skip + bad) + "/" + jobs.length + " (新下 " + ok + " 跳过 " + skip + " 失败 " + bad + ")");
  }
}
await Promise.all(Array.from({ length: CONC }, worker));
console.log("[dl] 完成: 新下 " + ok + " | 跳过 " + skip + " | 失败 " + bad);
