---
name: job-daily-search
description: Daily job search for Full Stack / AI Agent / Backend / Network developer positions from top remote job boards (Hacker News, Remote.co, Startup Jobs, Wellfound, FlexJobs, We Work Remotely). Use when the user asks to "search for jobs", "find job opportunities", "daily job search", "check job boards", or wants to discover remote developer positions matching their background. Prioritizes China-friendly remote positions (timezone + location allowed).
---

# Job Daily Search

每日从多个顶级远程招聘网站搜索匹配用户背景的软件开发职位，优先筛选对中国区友好的远程岗位。

## 用户背景（Danny Wang）

参考：`MEMORY.md` 中的简历链接和职位意向

- **职位目标**：Full Stack Engineer / AI Agent Engineer / Backend Engineer / Blockchain Engineer / Network Engineer
- **技术栈**：C++, Node.js, React, Python, Golang, Solidity, Smart Contracts, LLM Integration, Agent Framework
- **优先级**：AI Agent > Blockchain > Full Stack with AI > Backend > Network
- **地理要求**：Remote 职位必须允许 Chinese timezone 或明确支持中国区

## 核心流程

### 1. 搜索目标网站

按优先级顺序搜索以下网站（优先使用 `web_fetch`，失败时用 `browser`）：

1. **Hacker News "Who is Hiring?"** - https://news.ycombinator.com/jobs
   - 每月 1 号发布新帖，质量极高
   - 搜索关键词：AI Agent, Blockchain, Web3, Full Stack, Backend, Remote, China, Asia

2. **Remote.co** - https://remote.co/remote-jobs/developer/
   - 国际 remote 职位
   - 筛选：Developer 类别

3. **Startup Jobs** - https://startup.jobs/
   - 创业公司职位
   - 搜索：AI, Agent, Blockchain, Web3, Full Stack

4. **Wellfound (AngelList)** - https://wellfound.com/role/l/software-engineer
   - AI/LLM 初创公司集中
   - 搜索：AI Agent Engineer, Blockchain Engineer, Full Stack

5. **FlexJobs** - https://www.flexjobs.com/
   - 需付费会员，质量高
   - （可选，需登录）

6. **We Work Remotely** - https://weworkremotely.com/categories/remote-full-stack-programming-jobs
   - 专业 remote 职位
   - 分类：Full Stack, Backend

### 2. 职位筛选规则

**必须满足**：
- **发布时间**：7 天以内（排除老旧职位）
- Remote / Distributed / Work from anywhere
- 明确允许 Asia / China / Chinese timezone 或 "timezone flexible"
- 匹配技术栈（C++ / Node.js / React / Python / Golang / Solidity / Smart Contracts / LLM / Agent）

**优先级排序**：
1. **发布 1-3 天内**的职位（最新、最活跃）
2. 明确标注 "China OK" / "Asia timezone" 的职位
3. AI Agent Engineer / LLM Engineer 职位
4. Blockchain Engineer / Smart Contract Developer 职位
5. Full Stack with AI/Blockchain 经验要求
6. Backend Engineer（C++/Golang/Python/Node.js）
7. Network Engineer

**排除**：
- **发布超过 7 天的职位**（可能已招满）
- US-only / Europe-only（明确限制地理位置）
- On-site / Hybrid（非全远程）
- 不匹配技术栈的职位

### 3. 提取职位信息

对每个职位提取：
- **职位标题**
- **公司名称**
- **技术栈**
- **地理要求**（Remote policy）
- **薪资范围**（如有）
- **职位链接**

### 4. 输出格式

返回 **Top 5 匹配职位**，按优先级排序：

```markdown
## 📋 今日推荐职位（Top 5）

### 1. [职位标题] - [公司名称]
- **技术栈**：Node.js, React, LLM
- **地理要求**：Remote (China OK / Asia timezone)
- **薪资**：$120k-180k + equity
- **来源**：Hacker News
- **链接**：[Apply](https://...)
- **匹配度**：⭐⭐⭐⭐⭐ (AI Agent Engineer)

### 2. ...
```

## 实现方式

### 时间筛选

所有搜索必须过滤发布时间：
- 提取职位发布时间（如 "1d ago", "3 days ago", "posted 5 days ago"）
- 计算天数，**只保留 7 天以内的职位**
- 优先返回 1-3 天内的职位

### 优先使用 web_fetch

对静态页面优先用 `web_fetch` 提取内容：

```javascript
web_fetch(url, extractMode: "markdown")
```

提取 markdown 后用正则/文本匹配筛选职位。

### 备用 browser

当 `web_fetch` 不支持（如需 JS 渲染、登录）时用 `browser`：

```javascript
browser(action: "open", url: <target>, profile: "openclaw")
browser(action: "snapshot") // 或 evaluate 提取职位列表
```

## 搜索策略

### Hacker News Jobs

- URL：https://news.ycombinator.com/jobs
- 用 `web_fetch` 提取页面
- 搜索关键词：`AI Agent`, `Blockchain`, `Web3`, `Smart Contract`, `Full Stack`, `Remote`, `China`, `Asia`
- 筛选：包含 "Remote" 且未排除 China/Asia 的职位

### Remote.co

- URL：https://remote.co/remote-jobs/developer/
- 用 `web_fetch` 或 `browser` 提取职位列表
- 筛选：Developer 类别，匹配技术栈

### Startup Jobs / Wellfound

- 用 `browser` 搜索（可能需要 JS 渲染）
- 搜索关键词：AI Agent, Blockchain, Web3, Full Stack, Backend
- 筛选：Remote + 技术栈匹配

### We Work Remotely

- URL：https://weworkremotely.com/categories/remote-full-stack-programming-jobs
- 用 `web_fetch` 或 `browser` 提取职位列表
- **提取发布时间**（如 "1d", "5d", "15d"）
- **过滤**：只保留 7 天以内的职位（1d-7d）
- 筛选：Full Stack / Backend 分类

## 常见问题

### 如何判断职位是否支持中国区？

**明确支持**：
- "Remote (Worldwide)" / "Work from anywhere"
- "Asia timezone" / "Chinese timezone OK"
- "We hire globally"

**可能支持**（需进一步确认）：
- "Remote" 但未明确限制地区
- "Timezone flexible"

**明确不支持**：
- "US-only" / "Europe-only"
- "Must be in EST/PST timezone"
- "On-site in [city]"

### 技术栈匹配逻辑

**强匹配**（优先）：
- AI Agent / LLM / LangChain / OpenClaw / AutoGPT
- Blockchain / Web3 / Smart Contracts / Solidity / Rust
- Full Stack (Node.js + React)
- Backend (C++ / Python / Golang / Node.js)
- Systems Programming (C++ / Distributed Systems)

**次匹配**：
- Frontend (React / Vue / Next.js)
- Network (分布式系统 / API 设计)

**不匹配**（排除）：
- Java / Mobile (iOS/Android) 为主
- DevOps / SRE 专项（除非涉及 Backend）

## 输出示例

参考 `references/output-example.md`

## 限制

- **web_fetch** 限制：无法处理需要 JS 渲染或登录的网站（如 FlexJobs、部分 Wellfound 页面）
- **browser** 备用：当 web_fetch 失败时使用，但速度较慢
- **搜索频率**：建议每日执行 1 次（避免重复搜索）
