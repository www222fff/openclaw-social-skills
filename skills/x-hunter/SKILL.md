---
name: X Hunter - OpenClaw Deep Insights to X
description: 从 GitHub OpenClaw 仓库深度分析版本更新和社区讨论，生成有观点、有争议、有故事感的 X 帖子。触发词：「X hunter 发帖」「生成一条 X 帖子」「帮我发一条 OpenClaw 深度分析帖」
---

# 🛠️ X Hunter: OpenClaw Deep Insights to X

自动化流程：OpenClaw 仓库抓取 → **深度分析**（争议点/趋势/观点）→ 生成有料的帖子 → 发布到 X

**信息源**：GitHub OpenClaw 仓库（版本更新 + Issue 讨论 + 评论内容）

**核心升级**：不只统计数据，挖掘**争议点、趋势、反直觉观点**

---

## 🚀 触发方式

用户说：
- 「X hunter 发帖」
- 「生成一条 X 帖子」
- 「帮我发一条 OpenClaw 深度分析帖」
- 「X hunter 跑一次」

---

## 📝 完整流程（6步）

### Step 1: 抓取 OpenClaw 仓库信息

#### 1.1 版本更新（Releases）

```javascript
// 导航到 OpenClaw Releases 页面
browser navigate url=https://github.com/openclaw/openclaw/releases profile=openclaw

// 等待 3 秒后抓取最新 1-2 个版本的完整内容
browser evaluate javaScript=(()=>{
  return new Promise(r => setTimeout(() => {
    const sections = [...document.querySelectorAll('section')];
    const releases = sections.filter(s => s.querySelector('h2')).slice(0, 2).map(section => {
      const h2 = section.querySelector('h2');
      const version = h2?.innerText?.trim() || '';
      const body = section.innerText.slice(0, 800);
      return { source: 'Release', version: version, description: body };
    });
    r(releases);
  }, 3000));
})() profile=openclaw
```

**抓取要点**：
- 最新 1-2 个版本（足够覆盖近期更新）
- 截取前 800 字符描述（保留足够上下文）

#### 1.2 热门 Issue 讨论（标题 + 评论数）

```javascript
// 导航到 OpenClaw Issues 页面（按评论数排序）
browser navigate url=https://github.com/openclaw/openclaw/issues?q=is%3Aissue+is%3Aopen+sort%3Acomments-desc profile=openclaw

// 等待 3 秒后抓取前 5 条热门 Issue
browser evaluate javaScript=(()=>{
  return new Promise(r => setTimeout(() => {
    const text = document.body.innerText;
    // 手动提取 Issue 信息（从页面文本中解析）
    r({ issuesText: text.slice(0, 2000) });
  }, 3000));
})() profile=openclaw
```

**抓取策略**：先拿到页面文本，再从中提取 Issue 编号、标题、评论数

#### 1.3 深度抓取：Issue 评论内容（核心升级！）

选取评论数最高的 **1-2 个 Issue**，进入详情页抓取前 5-10 条评论：

```javascript
// 导航到具体 Issue 页面（例如 #3460）
browser navigate url=https://github.com/openclaw/openclaw/issues/3460 profile=openclaw

// 等待 3 秒后抓取评论内容
browser evaluate javaScript=(()=>{
  return new Promise(r => setTimeout(() => {
    const comments = [...document.querySelectorAll('.comment-body')].slice(0, 10).map(c => {
      return c.innerText.slice(0, 300);
    });
    r({ issue: '#3460', comments: comments });
  }, 3000));
})() profile=openclaw
```

**抓取要点**：
- 取前 5-10 条评论（代表性观点）
- 每条截取 300 字符（提取核心论点）
- 识别**争议点**（对立观点、分歧、反对声音）

---

### Step 2: 深度分析（核心升级！）

从抓取结果中进行**多维度分析**：

#### 2.1 版本更新热点筛选

从 Release notes 中识别：
1. **新工具/新能力**（扩展边界）
2. **Breaking changes**（影响所有用户）
3. **重大性能提升**（体验改善）
4. **社区呼声 Feature**（解决痛点）

**判断标准**：
- 有重大特性 → 发版本更新帖
- 都是小修小补 → 跳过，聚焦 Issue

#### 2.2 Issue 趋势分析

从热门 Issue 中提炼**模式**：

**地域模式**：
- DingTalk/Feishu → 中国市场需求
- Linux/Windows apps → 跨平台需求
- i18n → 全球化需求

**类型模式**：
- Feature request 多 → 扩张期
- Bug report 多 → 稳定性危机
- Discussion 多 → 架构/方向争议

**时间模式**：
- 某 Issue 评论突增 → 痛点爆发
- 某类 Issue 持续高热 → 长期需求

#### 2.3 评论争议点挖掘

从评论内容中识别**对立观点**：

**常见争议类型**：
- 优先级之争（"先修 bug" vs "先加功能"）
- 路径之争（"全面重构" vs "渐进优化"）
- 场景之争（"企业用户" vs "个人开发者"）
- 技术之争（"云优先" vs "本地优先"）

**提取方法**：
- 找 "but", "however", "disagree" 等转折词
- 找重复出现的关键词（高频争议点）
- 找情绪强烈的表达（"must", "critical", "broken"）

#### 2.4 观点生成策略

基于分析结果，选择**帖子类型**：

| 分析结果 | 帖子类型 | 核心策略 |
|---------|---------|---------|
| 评论有明显分歧 | **争议帖** | 展示双方观点 + 提出判断 |
| 多个 Issue 有共同模式 | **趋势帖** | 提炼模式 + 预测方向 |
| 不同地域/场景需求差异大 | **对比帖** | 制造反差 + 引发思考 |
| Issue 变化轨迹明显 | **时间线帖** | 讲述演进 + 揭示转折 |
| 主流观点有漏洞 | **挑战帖** | 提出反直觉观点 |
| Issue 连接行业大势 | **连接帖** | 升华格局 + 行业视角 |

---

### Step 3: 生成有观点的帖子

**严格控制在 280 字符以内**（X 免费账户限制）

#### 类型 1：争议帖 🔥

**模板**：
```
[Issue话题] (#编号, X comments):

"[观点A]" vs "[观点B]"

[你的判断]

[一句话总结争议本质]
```

**示例**：
```
OpenClaw's i18n debate (#3460, 101 comments):

"Build for global first" vs "Fix core bugs first"

Both valid. But here's the thing:
Agents need universal *tool* access > UI translation

Localization ≠ Going global 🌍
```

#### 类型 2：趋势帖 📊

**模板**：
```
[观察对象]'s top [N] asks tell a story:

→ [Issue1标题] ([评论数])
→ [Issue2标题] ([评论数])
→ [Issue3标题] ([评论数])

Pattern? [提炼的趋势]

[一句话判断/预测]
```

**示例**：
```
OpenClaw's top 4 asks tell a story:

→ i18n (101)
→ DingTalk (67)  
→ Desktop apps (38)

Pattern? Expansion.

Community pushing beyond dev tools → mass market 🚀
```

#### 类型 3：对比帖 ⚡

**模板**：
```
What different [维度] want from [产品]:

[维度A]: [需求A]
[维度B]: [需求B]

Same tool, different worlds [emoji]

[一句话升华]
```

**示例**：
```
What different markets want from OpenClaw:

🇺🇸 West: Linux apps, self-hosting
🇨🇳 China: DingTalk, Feishu integration

Same tool, different worlds 🌏

Agent adoption = culture fit, not just features
```

#### 类型 4：时间线帖 ⏱️

**模板**：
```
[Issue话题] (#编号):

[时间1]: [状态1]
[时间2]: [状态2]

What changed? [转折点分析]

[一句话总结]
```

**示例**：
```
OpenClaw i18n (#3460):

3 months ago: "Nice to have"
Today: 101 comments, top ask

What changed? Users realized:
Agents work in *every* language, not just English 🌍

Stakes just got higher
```

#### 类型 5：挑战帖 🤔

**模板**：
```
Hot take on [话题] (#编号, X comments):

[主流观点]

But maybe [反直觉观点]:
→ [论据1]
→ [论据2]

[一句话挑战常识]
```

**示例**：
```
Hot take on OpenClaw's i18n debate (#3460, 101 comments):

Everyone wants localized UIs

But agents need:
→ Multi-language *tool* docs
→ Cross-border API access

Translating menus ≠ going global 🌍
```

#### 类型 6：连接帖 🌐

**模板**：
```
Why [Issue话题] (#编号, X comments) matters:

[行业数据/大势]

[一句话连接]

[升华格局的判断]
```

**示例**：
```
Why OpenClaw's DingTalk ask (#26534, 67 comments) matters:

China enterprise = 400M+ users
DingTalk/Feishu > Slack globally

If AI agents don't integrate, they stay a Western niche 🌏

Real race: Who goes global first?
```

---

### Step 4: 生成配图（可选）

为了提高互动率，可以截图 GitHub 页面作为配图：

```javascript
// 截图当前 Issue 或 Releases 页面
browser screenshot profile=openclaw type=png

// 截图会自动保存
```

**或者跳过配图**（纯文字发帖）。

---

### Step 5: 发布到 X

**⚠️ 关键**：X 使用 Draft.js 编辑器，**必须用 clipboard + Ctrl+V** 方式输入。

```javascript
// 1. 导航到发帖页
browser navigate url=https://x.com/compose/post profile=openclaw

// 2. 如果有截图，先上传图片（可选，暂需手动）

// 3. 等待 2 秒后，写入剪贴板并粘贴文字
browser evaluate javaScript=(()=>{
  return new Promise(r => setTimeout(() => {
    const post = `你生成的帖子内容（≤280字符）`;
    
    const textarea = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (!textarea) return r({ error: 'no textarea' });
    
    textarea.focus();
    
    navigator.clipboard.writeText(post).then(() => {
      r({ copied: true, length: post.length });
    });
  }, 2000));
})() profile=openclaw

// 4. 模拟 Ctrl+V 粘贴
browser act kind=press key=Control+v profile=openclaw

// 5. 等待 1 秒，验证内容是否已填入
browser evaluate javaScript=(()=>{
  return new Promise(r => setTimeout(() => {
    const textarea = document.querySelector('[data-testid="tweetTextarea_0"]');
    const btn = document.querySelector('[data-testid="tweetButton"]');
    r({ 
      text: textarea?.innerText,
      length: textarea?.innerText?.length,
      btnDisabled: btn?.disabled
    });
  }, 1000));
})() profile=openclaw

// 6. 点击发送（如果按钮已启用）
browser evaluate javaScript=(()=>{
  const btn = document.querySelector('[data-testid="tweetButton"]');
  if (btn && !btn.disabled) {
    btn.click();
    return { clicked: true };
  }
  return { error: 'btn disabled or not found' };
})() profile=openclaw
```

---

## ⚠️ 重要注意事项

1. **字符限制**：X 免费账户 280 字符，超过会被截断
2. **输入方式**：必须用 clipboard + Ctrl+V（Draft.js 限制）
3. **browser profile**：必须使用 `openclaw`（已登录 X 账号）
4. **等待时间**：每步之间加 1-3 秒延迟，避免 DOM 未加载完成
5. **验证发送**：检查 `clicked: true` 确认发送成功
6. **深度分析优先级**：争议点 > 趋势模式 > 单纯统计
7. **配图（推荐）**：截图 GitHub 页面提高互动率

---

## 🎯 内容风格指南（升级版）

### 必须做到
- ✅ **有观点**：不只陈述事实，提出判断
- ✅ **有争议**：展示分歧，引发讨论
- ✅ **有故事**：用对比、转折、反差制造张力
- ✅ **有连接**：升华到行业/趋势/文化层面
- ✅ **可验证**：Issue 编号、评论数必须真实

### 必须避免
- ❌ 纯统计（"Top 5 issues are..."）
- ❌ 无观点（只罗列不判断）
- ❌ 泛泛而谈（"很重要"、"值得关注"）
- ❌ 过度营销（"最强"、"必用"）

### 帖子选择优先级
1. **争议帖**（有明显分歧） - 互动率最高
2. **对比帖**（地域/场景差异） - 制造反差
3. **挑战帖**（反直觉观点） - 引发争论
4. **趋势帖**（模式提炼） - 显示洞察
5. **连接帖**（行业视角） - 升华格局
6. **时间线帖**（变化轨迹） - 讲述故事

---

## 📊 信息源总结

| 来源 | 内容 | 数量 | 深度 |
|------|-----|------|------|
| **Releases** | 版本更新 | 1-2 个版本 | 筛选重大特性 |
| **Issues（概览）** | 热门讨论 | 前 5 条 | 标题 + 评论数 |
| **Issues（详情）** | 评论内容 | 1-2 个最热 Issue | 前 5-10 条评论 |

**分析维度**：
- 🔥 争议点（对立观点）
- 📊 趋势（地域/类型/时间模式）
- 🤔 反直觉（挑战主流观点）
- 🌐 连接（行业大势）

---

## 📬 Support

- **X (Twitter):** @CrossoverYao（已登录 openclaw profile）
- **OpenClaw Repo:** https://github.com/openclaw/openclaw
