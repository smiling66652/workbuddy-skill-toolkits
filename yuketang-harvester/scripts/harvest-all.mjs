// 全课程课件采集器（带断点续传）
// 用法:
//   node harvest-all.mjs index     仅建索引（课程→课时→课件）
//   node harvest-all.mjs text      抓取全部课件的文字层（shapes[].Text）
//   node harvest-all.mjs           两步都跑
// 依赖: CDP Proxy 已在 127.0.0.1:3456，浏览器已登录 changjiang.yuketang.cn
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const PORT = 3456;
const OUT = "D:/桌面/浏览器/yuketang-research";
const DATA = path.join(OUT, "harvest");
const TEXTS = path.join(DATA, "texts");
fs.mkdirSync(TEXTS, { recursive: true });
const INDEX = path.join(DATA, "index.json");

function req(method, p, body) {
  return new Promise((res, rej) => {
    const opt = { host: "127.0.0.1", port: PORT, path: p, method, timeout: 120000 };
    if (body != null) opt.headers = { "Content-Type": "text/plain;charset=utf-8", "Content-Length": Buffer.byteLength(body) };
    const r = http.request(opt, (resp) => { let d = ""; resp.on("data", (c) => (d += c)); resp.on("end", () => res(d)); });
    r.on("timeout", () => { r.destroy(); rej(new Error("timeout " + p)); });
    r.on("error", rej);
    if (body != null) r.write(body);
    r.end();
  });
}

async function target() {
  const raw = await req("GET", "/targets");
  let arr = []; try { arr = JSON.parse(raw); } catch (e) {}
  const t = arr.find((x) => /yuketang\.cn/.test(x.url || ""));
  if (!t) throw new Error("no yuketang tab");
  return t.targetId;
}

async function ev(tid, js) {
  const out = await req("POST", "/eval?target=" + tid, js);
  let o; try { o = JSON.parse(out); } catch (e) { throw new Error("bad eval resp: " + out.slice(0, 200)); }
  if (o.error) throw new Error(o.error);
  return typeof o.value === "string" ? JSON.parse(o.value) : o.value;
}

const PRELUDE = `const tk=localStorage.getItem("Authorization")||"";
const H={Accept:"application/json, text/plain, */*",Authorization:"Bearer "+tk,"X-Client":"h5",xtbz:"ykt"};
const j=async u=>{const r=await fetch(u,{credentials:"include",headers:H});const t=await r.text();try{return JSON.parse(t)}catch(e){return{__err:t.slice(0,120),__s:r.status}}};`;

async function buildIndex(tid) {
  const js = `(async()=>{${PRELUDE}
    const cl=await j("/v2/api/web/courses/list?identity=2");
    const list=(cl.data&&cl.data.list)||[];
    const out=[];
    for(const c of list){
      const cid=c.classroom_id;
      const lg=await j("/v2/api/web/logs/learn/"+cid+"?actype=-1&page=0&offset=100&sort=-1");
      const acts=((lg.data&&lg.data.activities)||[]).filter(a=>a.type===14);
      if(!acts.length) continue;
      const lessons=[];
      for(const a of acts){
        const s=await j("/api/v3/lesson-summary/student?lesson_id="+a.courseware_id);
        const ps=((s.data&&s.data.presentations)||[]).map(p=>({pid:p.id,title:p.title,slides:p.slidesCount||0}));
        lessons.push({lessonId:a.courseware_id,title:a.title,ts:a.create_time,finished:a.is_finished,pres:ps});
      }
      out.push({cid,term:c.term,course:(c.course&&c.course.name)||"",className:c.name||"",teacher:(c.teacher&&c.teacher.name)||"",lessons});
    }
    return JSON.stringify({t:Date.now(),courses:out});
  })()`;
  const data = await ev(tid, js);
  fs.writeFileSync(INDEX, JSON.stringify(data, null, 1), "utf8");
  return data;
}

async function fetchText(tid, pid) {
  const js = `(async()=>{${PRELUDE}
    const r=await fetch("/api/v3/lesson/presentation/fetch?presentation_id=${pid}",{credentials:"include",headers:H});
    const t=await r.text();
    let d; try{ d=JSON.parse(t) }catch(e){ return JSON.stringify({__err:"parse",s:r.status}) }
    const dd=d.data||{};
    const slides=(dd.slides||[]).map(s=>({
      i:s.index, cover:s.cover,
      t:(s.shapes||[]).slice().sort((a,b)=>(a.ZOrderPosition||0)-(b.ZOrderPosition||0))
        .map(x=>(x.Text||"").replace(/\\u000b/g," ").replace(/\\r/g,"\\n").trim()).filter(Boolean)
    }));
    return JSON.stringify({title:dd.title,w:dd.width,h:dd.height,n:slides.length,slides});
  })()`;
  return ev(tid, js);
}

const mode = process.argv[2] || "all";
const tid = await target();
console.log("[harvest] target=" + tid);

if (mode === "index" || mode === "all") {
  console.log("[harvest] 建索引 …");
  const idx = await buildIndex(tid);
  const tot = idx.courses.reduce((a, c) => a + c.lessons.reduce((x, l) => x + l.pres.length, 0), 0);
  console.log("[harvest] 索引完成: " + idx.courses.length + " 门课 / " + tot + " 个课件");
}

if (mode === "text" || mode === "all") {
  const idx = JSON.parse(fs.readFileSync(INDEX, "utf8"));
  const jobs = [];
  for (const c of idx.courses) for (const l of c.lessons) for (const p of l.pres) jobs.push({ cid: c.cid, course: c.course, ...p });
  console.log("[harvest] 待抓课件 " + jobs.length + " 个");
  let ok = 0, skip = 0, bad = 0;
  for (const job of jobs) {
    const f = path.join(TEXTS, job.pid + ".json");
    if (fs.existsSync(f) && fs.statSync(f).size > 100) { skip++; continue; }
    try {
      const d = await fetchText(tid, job.pid);
      if (d && d.__err) { bad++; console.log("  ! " + job.pid + " " + d.__err); continue; }
      fs.writeFileSync(f, JSON.stringify({ ...job, ...d }), "utf8");
      ok++;
      if ((ok + skip) % 10 === 0) console.log("  进度 " + (ok + skip) + "/" + jobs.length + " (新抓 " + ok + " / 跳过 " + skip + " / 失败 " + bad + ")");
    } catch (e) { bad++; console.log("  x " + job.pid + " " + String(e).slice(0, 80)); }
  }
  console.log("[harvest] 完成: 新抓 " + ok + " | 跳过(已存在) " + skip + " | 失败 " + bad);
}
