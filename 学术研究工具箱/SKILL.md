---
name: 学术研究工具箱
description: >
  统一学术研究工具箱（三级层级结构）。一级：分析需求（找论文/写综述/管引用/做一手源调研）。
  二级：选择方法（数据库检索/综述结构化/BibTeX与Zotero/深度调研）。三级：读 references 执行。
  面向机械工程背景转电气/计算机方向的学生，覆盖 arXiv / Semantic Scholar / CNKI /
  IEEE Xplore / ScienceDirect / Google Scholar，强调每条结论必须附一手来源。
  触发词：论文、文献、检索、查文献、知网、CNKI、arXiv、IEEE、ScienceDirect、
  文献综述、怎么写综述、引用、参考文献、BibTeX、Zotero、调研、查资料、柔性抓取、
  阻抗控制、软体抓取、compliant grasp、impedance control、soft gripper
version: 1.0.0
author: Matebook
---

# 学术研究工具箱

> 解决的是「想做科研，但检索/综述/引用这条线没人带、效率低、还容易抄二手」的问题。
> 用户目前**最缺的就是这条线**：机械臂柔性抓取（番茄/鸡蛋 + 阻抗控制）的文献综述正在进行，项目申请书待做。

---

## 一级：判断当前需求

拿到任务先问：**我现在要的是哪一类？** 然后跳到对应 references。

| 你现在要做的事 | 跳到二级 | 读的文件 |
|---|---|---|
| 找论文 / 查文献 / 检索某主题 | 数据库检索 | `references/论文检索.md` |
| 写文献综述 / 不会搭框架 / 不会找 gap | 综述结构化 | `references/文献综述.md` |
| 管引用 / 导出参考文献 / BibTeX / Zotero | 引用管理 | `references/引用管理.md` |
| 做可信调研 / 拒绝二手编造 / 每条要溯源 | 一手源研究 | `references/一手源研究.md` |

> 多数真实任务会串起来：**检索 → 综述 → 引用** 是一气呵成的。先用 `论文检索.md` 把论文捞回来，用 `引用管理.md` 落库，再用 `文献综述.md` 组织成文。

---

## 二级：你的资源清单（合工大在校生特有优势，先用满）

你是**合肥工业大学**在读本科生，学校已购大量数据库，这是你比野路子检索最大的优势：

| 资源 | 怎么用 | 覆盖 |
|---|---|---|
| 合工大图书馆 / CARSI 统一认证 | 学校官网「数据库导航」或 CARSI 登录 | 校外也能直连订阅库 |
| **CNKI 知网**（CARSI） | 校园网/CARSI 直连，免费用 | 中文核心期刊、硕博论文、会议 |
| **IEEE Xplore**（学校订阅） | 校园网直连，机构已付费 | 电气/机器人/自动化顶会期刊 |
| **ScienceDirect / Elsevier**（学校订阅） | 校园网直连 | 机械/控制/材料期刊 |
| arXiv（开放，无需订阅） | 任意网络 | 最新预印本，机器人(cs.RO)更新极快 |
| Semantic Scholar（开放） | 任意网络 | 引文图谱、找「谁引用了谁」 |
| Google Scholar | 网络可达时用 | 补全网检索；**常被墙/验证码**，见降级方案 |

**本机环境（命令能直接抄）：**
- 系统：Windows 11 + Git Bash
- Python：`C:\Users\Matebook\.workbuddy\binaries\python\versions\3.13.12\python.exe`
- 已有工具：`联网工具箱/references/电子书下载.md`（教材/专著下载，原 `ebook-fetch` 能力已并入）、`course-search.py`（`D:\.workbuddy\tools\` 本地课程 BM25 检索）、文档工具箱 / 联网工具箱 / 知识工具箱

---

## 三级：铁律（与你的偏好一致）

> **每条结论必须附一手来源。** 来源 = 论文 DOI / 官方文档 URL / 源码文件:行号 / 标准编号。
> 二手转述、博客、以及「模型自己记得的」都**不算**证据。
> 无法追溯的内容，必须明确标 **「未验证」**，绝不允许写成确定结论。

- 写综述引用必须追到**原始论文**，不要引「某某综述说」。
- 调参/方法结论必须给**出处论文或官方文档**，不能凭印象。
- 命令、API 示例必须**实测或标注「未实测」**，禁止编造「能跑通」。

---

## 环境提示（校园网专属坑，务必照做）

> **校园网 curl 会卡证书吊销检查**，报 `schannel: CRYPT_E_NO_REVOCATION_CHECK` 或 `HTTP 000`。
> **所有 curl 命令一律加 `--ssl-no-revoke`** 才能通。

```bash
# 正确姿势：每个 curl 都带 --ssl-no-revoke
curl -s --ssl-no-revoke "https://api.semanticscholar.org/..." -o out.json
```

其它本机坑：
- **GitHub 下载常截断** → 下完用 `wc -c` / `ls -l` 校验字节数，不对就重下。
- **`raw.githubusercontent.com` 常被墙** → 优先用镜像 `https://cdn.jsdelivr.net/gh/<user>/<repo>@<branch>/<path>`。

---

## 实测状态速览（本包撰写时的真实测试结果，非虚构）

本包所有命令行示例均按「拒绝模拟数据」原则处理。撰写环境为**非校园网沙箱**，实测如下：

| 接口 | 撰写时实测 | 说明 |
|---|---|---|
| **DOI → BibTeX**（doi.org 内容协商） | ✅ HTTP 200，返回合法 BibTeX | 已真实验证，命令可直接用 |
| **Semantic Scholar** `/paper/search` | ⚠️ HTTP 429（接口可达，被限流） | 语法正确；匿名限流严，建议申请免费 API key |
| **arXiv** `export.arxiv.org` | ❌ HTTP 000（沙箱屏蔽该域名） | 开放免费，**校园网可直接用**；命令语法按官方文档核对 |
| **Google Scholar** | ❌ HTTP 000（被屏蔽） | 校园网也常遇验证码；用 `论文检索.md` 的降级方案 |
| **CNKI / IEEE / ScienceDirect** | 无法在沙箱外网测 | 需校园订阅/API key；按 `论文检索.md` 给的官方端点与策略操作 |

> 凡标注「撰写时未实测」的命令，语法均依据对应官方文档，请你在**校园网**上第一次使用前先跑一遍确认。

---

## 触发后怎么做

1. 先定位一级需求（上表）。
2. 读对应的 `references/*.md`，按里面的**可直接复制命令**和**模板**执行。
3. 检索到的论文立刻用 `references/引用管理.md` 的 DOI→BibTeX 落库到 Zotero。
4. 成文阶段用 `references/文献综述.md` 的分类体系和对比表模板。
5. 任何结论都按 `references/一手源研究.md` 的「结论+证据+置信度」格式留痕。
