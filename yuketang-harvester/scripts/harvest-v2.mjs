// 双通道课件采集：优先 presentation/fetch（有文字层），失败则回退 lesson-summary/student/presentation（仅页图）
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const PORT = 3456;
const OUT = "D:/桌面/浏览器/yuketang-research";
const DATA = path.join(OUT, "harvest");
const SL = path.join(DATA, "slides");
fs.mkdirSync(SL, { recursive: true });
const INDEX = path.join(DATA, "index.json");

function req(method, p, body) {
  return new Promise((res, rej) => {
    const opt = { host: "127.0.0.1", port: PORT, path: p, method, timeout: 120000 };
    if (body != null) opt.headers = { "Content-Type": "text/plain;charset=utf-8", "Content-Length": Buffer.byteLength(body) };
    const r = http.request(opt, (resp) => { let d = ""; resp.on("data", (c) => (d += c)); resp.on("end", () => res(d)); });
    r.on("timeout", () => { r.destroy(); rej(new Error("timeout")); });
    r.on("error", rej);
    if (body != null) r.write(body);
    r.end();
  });
}
async function ev(js) {
  const raw = await req("GET", "/targets");
  const t = JSON.parse(raw).find((x) => /yuketang\.cn/.test(x.url || ""));
  const out = await req("POST", "/eval?target=" + t.targetId, js);
  const o = JSON.parse(out);
  if (o.error) throw new Error(o.error);
  return typeof o.value === "string" ? JSON.parse(o.value) : o.value;
}

const js = (pid, lid) => `(async () => {
  const tk = localStorage.getItem("Authorization") || "";
  const H = { "Accept": "application/json, text/plain, */*", "Authorization": "Bearer " + tk, "X-Client": "h5", "xtbz": "ykt" };
  const g = async u => { const r = await fetch(u, { credentials: "include", headers: H }); const t = await r.text(); try { return JSON.parse(t); } catch (e) { return { __err: t.slice(0, 100) }; } };

  // 通道 A：有文字层
  const a = await g("/api/v3/lesson/presentation/fetch?presentation_id=${pid}");
  if (a && a.code === 0 && a.data && a.data.slides && a.data.slides.length) {
    const dd = a.data;
    const slides = dd.slides.map(s => ({
      i: s.index, cover: s.cover,
      t: (s.shapes || []).slice().sort((x, y) => (x.ZOrderPosition || 0) - (y.ZOrderPosition || 0))
        .map(z => (z.Text || "").replace(/\\u000b/g, " ").replace(/\\r/g, "\\n").trim()).filter(Boolean)
    }));
    return JSON.stringify({ mode: "text", title: dd.title, w: dd.width, h: dd.height, slides });
  }

  // 通道 B：仅页图（旧学期课件走这里）
  const b = await g("/api/v3/lesson-summary/student/presentation?presentation_id=${pid}&lesson_id=${lid}");
  if (b && b.code === 0 && b.data && b.data.slides) {
    const dd = b.data;
    const slides = dd.slides.map(s => ({ i: s.index, cover: s.cover, t: [], problem: s.problem || null }));
    return JSON.stringify({ mode: "image", title: (dd.presentation || {}).title || "", w: (dd.presentation || {}).width, h: (dd.presentation || {}).height, slides });
  }
  return JSON.stringify({ mode: "fail", a_code: a && a.code, a_msg: a && a.msg, b_code: b && b.code, b_msg: b && b.msg });
})()`;

const idx = JSON.parse(fs.readFileSync(INDEX, "utf8"));
const jobs = [];
for (const c of idx.courses) for (const l of c.lessons) for (const p of l.pres) jobs.push({ cid: c.cid, course: c.course, lessonId: l.lessonId, pid: p.pid, title: p.title });

let text = 0, image = 0, skip = 0, fail = 0;
const i = 0;
for (const job of jobs) {
  const f = path.join(SL, job.pid + ".json");
  if (fs.existsSync(f) && fs.statSync(f).size > 200) { skip++; continue; }
  try {
    const d = await ev(js(job.pid, job.lessonId));
    if (d.mode === "fail") { fail++; console.log("  ! " + job.course + " " + job.pid + " " + d.a_msg + "/" + d.b_msg); continue; }
    fs.writeFileSync(f, JSON.stringify({ ...job, ...d }), "utf8");
    if (d.mode === "text") text++; else image++;
    if ((text + image) % 10 === 0) console.log("  进度 " + (text + image + skip) + "/" + jobs.length + " | 文字 " + text + " 页图 " + image + " 跳过 " + skip + " 失败 " + fail);
  } catch (e) { fail++; console.log("  x " + job.pid + " " + String(e).slice(0, 70)); }
}
console.log("完成: 文字型 " + text + " | 页图型 " + image + " | 跳过 " + skip + " | 失败 " + fail);
