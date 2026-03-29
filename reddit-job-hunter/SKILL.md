---
name: reddit-job-hunter
description: 在 Reddit 上搜索招聘帖子并私信招聘方。当用户说「去 Reddit 找工作」「帮我在 Reddit 上找招聘」「Reddit 求职」「Reddit DM 招聘」或涉及 Reddit 职位搜索+私信联系的任务时触发本 skill。
---

# Reddit Job Hunter

在 Reddit 招聘板块搜索匹配用户背景的职位，筛选真实招聘帖（排除 job board bot），并向招聘方发送私信。

## 前置条件

1. 托管浏览器 profile=openclaw 已启动并配置代理（访问 Reddit 需要）
2. Reddit 账号已在托管浏览器中登录
3. 用户简历/背景信息已知（参考 MEMORY.md 或用户提供）

## 核心流程

### 1. 打开 Reddit 并确认登录

```
browser open url=https://www.reddit.com profile=openclaw
evaluate: 检查 hasUserMenu 或 hasLoginBtn 判断登录状态
```

若未登录，提示用户先手动登录。

### 2. 搜索招聘帖

**推荐 subreddit**：
- r/forhire（[Hiring] 标签帖子，综合职位）
- r/DeveloperJobs（开发者专项，活跃度高）
- r/AIJobs（AI/ML 相关职位）
- r/remotejs（JavaScript/Node.js 技术栈专项）
- 全站搜索：`/search/?q="hiring" "engineer"&sort=new&t=week`

**高匹配关键词（优先搜索）**：

**AI Agent 方向**：
- "AI agent" / "agent framework" / "autonomous agent"
- "OpenClaw" / "Claw" / "agent orchestration"
- "LangChain" / "AutoGPT" / "CrewAI" / "Haystack"
- "multi-agent system" / "agent automation"
- "prompt engineering" / "RAG" / "vector database"

**后端/系统方向**：
- "backend" / "full stack" / "fullstack"
- "C++" / "system programming" / "low-level"
- "database" / "SQL" / "PostgreSQL" / "MongoDB"
- "network" / "telecom" / "core network" / "5G"
- "distributed system" / "microservices"

**搜索示例**：
```
# AI Agent 专项
navigate: https://www.reddit.com/search/?q=hiring%20"AI%20agent"&sort=new&t=month
navigate: https://www.reddit.com/r/AIJobs/search/?q=agent%20framework&sort=new&t=week

# 后端/全栈
navigate: https://www.reddit.com/r/DeveloperJobs/search/?q=backend%20OR%20fullstack&sort=new&t=week
navigate: https://www.reddit.com/r/forhire/search/?q=hiring%20C%2B%2B&sort=new&t=week

# 系统/网络
navigate: https://www.reddit.com/search/?q=hiring%20database%20engineer&sort=new&t=month
navigate: https://www.reddit.com/search/?q=hiring%20network%20telecom&sort=new&t=month
```

### 3. 筛选职位

用 evaluate 提取帖子列表：
```javascript
[...document.querySelectorAll('a[href*="/comments/"]')]
  .map(a => ({ href: a.href, text: a.innerText.slice(0, 120) }))
  .filter(p => /hiring/i.test(p.text))
```

**排除 bot 账号**：
- 检查发帖人 profile，若全是 job board 聚合帖（如 u/rrmdp, u/Varqu）则跳过
- 优先选择：帖子有具体职位描述、发帖人有个人资料、非批量转发

**职位匹配度评分（优先级）**：
1. **高匹配**（优先联系）：
   - **AI Agent 方向**：AI agent / agent framework / OpenClaw / LangChain / RAG / prompt engineering
   - **后端/系统方向**：Backend / Full Stack / C++ / Database / Network / Telecom Core Network
   - **技术栈**：Python + LLM + 自动化 / 编排，或 C++ 系统开发
   - **团队类型**：小团队 / 创业公司（更看重实战能力）
   
2. **中匹配**（可以尝试）：
   - 全栈 + AI 集成（但不是核心 AI agent）
   - 后端 + Python + 自动化（但无 AI）
   - JavaScript/Node.js 全栈开发
   - 提到 vector database / API 集成 / 性能优化
   
3. **低匹配**（谨慎选择）：
   - 纯前端 / 纯 QA / 纯测试
   - 大公司标准岗（更看重学历/年限，不看重实战）
   - 薪资明显不合理（过低 <$20/hr 或 equity only 无现金）
   - 技术栈完全不匹配（如纯 Java/C#/.NET，无 Python/C++/Node.js）

### 4. 查看职位详情

导航到具体帖子，提取职位要求：
```javascript
document.body.innerText.slice(0, 2000)
```

判断是否匹配用户背景（技术栈、经验年限、remote/onsite）。

### 5. 私信招聘方

**🚨 警告：发错人是严重错误，必须严格执行以下验证流程**

**进入用户 profile 页**：
```
navigate: https://www.reddit.com/user/<username>
```

**⚠️ 关键：必须点击 Profile 页面的 "Start Chat" 链接（不是顶部导航的 "Open chat" 按钮）**：

Reddit profile 页面的 "Start Chat" 是一个 `<a>` 标签（不是 button），位于右侧边栏。

```javascript
// 正确方式：查找右侧边栏的 "Start Chat" 链接
const allLinks = [...document.querySelectorAll('a')];
const startChatLink = allLinks.find(a => a.innerText?.trim() === 'Start Chat');

if (startChatLink) {
  startChatLink.click();
  // 点击后会打开 Shadow DOM 聊天窗口，不会跳转页面
} else {
  throw new Error('Cannot find "Start Chat" link on profile page');
}
```

**为什么不能用 "Open chat" 按钮**：
- 顶部导航的 "Open chat" 会打开最近的聊天记录
- 可能打开错误的聊天对象（上一个联系人）
- 必须用 profile 页面的 "Start Chat" 才能确保与目标用户对话

**⚠️ 验证聊天对象（强制执行，发错人是严重错误）**：
```javascript
function findInShadow(root, selector, depth = 0) {
  if (depth > 10) return [];
  const results = [...root.querySelectorAll(selector)];
  const hosts = [...root.querySelectorAll('*')].filter(el => el.shadowRoot);
  for (const host of hosts) {
    results.push(...findInShadow(host.shadowRoot, selector, depth + 1));
  }
  return results;
}

// 等待聊天窗口加载（最多 3 秒）
await new Promise(r => setTimeout(r, 2000));

// ⚠️ 关键：检查聊天窗口中是否包含目标用户名
const allElements = findInShadow(document, '*');
const allText = allElements.map(el => el.innerText || '').join(' ');
const targetUsername = 'username'; // ⚠️ 必须替换为实际用户名（如 "Dense-Try-7798"）

if (!allText.includes(targetUsername)) {
  // 发错人是严重错误，必须抛错停止
  throw new Error(`❌ CRITICAL: Chat recipient verification FAILED - expected u/${targetUsername}, but window shows different user. STOP and close chat.`);
}

console.log(`✅ Chat recipient verified: u/${targetUsername}`);

// ⚠️ 双重验证：再检查一次 URL 或窗口标题
// 确保聊天对象 100% 正确，绝对不能发错人
```

**填写消息并发送**（Reddit 使用 Shadow DOM，需递归搜索）：
```javascript
function findInShadow(root, selector, depth = 0) {
  if (depth > 10) return [];
  const results = [...root.querySelectorAll(selector)];
  const hosts = [...root.querySelectorAll('*')].filter(el => el.shadowRoot);
  for (const host of hosts) {
    results.push(...findInShadow(host.shadowRoot, selector, depth + 1));
  }
  return results;
}

// 1. 填入消息
const textareas = findInShadow(document, 'textarea');
const chatTa = textareas.find(ta => ta.placeholder === 'Message');
chatTa.focus();
chatTa.value = "<消息内容>";
chatTa.dispatchEvent(new Event('input', { bubbles: true }));
chatTa.dispatchEvent(new Event('change', { bubbles: true }));

// 2. ⚠️ 发送消息：必须使用键盘快捷键 Ctrl+Enter
// ⚠️ 重要：不要尝试点击发送按钮，直接用 Ctrl+Enter
// Reddit 聊天输入框右侧有飞机图标按钮（SVG icon），但键盘事件更可靠
chatTa.focus();
chatTa.dispatchEvent(new KeyboardEvent('keydown', {
  key: 'Enter',
  code: 'Enter',
  keyCode: 13,
  ctrlKey: true,
  bubbles: true
}));

// ⚠️ 不推荐：查找按钮并点击（有时不触发）
// const allBtns = findInShadow(document, 'button');
// const submitBtn = allBtns.find(b => b.innerText?.includes('Submit'));
// if (submitBtn) submitBtn.click();
```

**为什么用 Ctrl+Enter 而不是点击按钮**：
- Reddit 聊天输入框右侧有飞机图标（SVG）发送按钮
- 但按钮点击事件有时不触发（可能需要特定条件才 enable）
- **Ctrl+Enter 键盘事件最可靠**，能直接触发发送逻辑

### 6. 验证发送成功

检查 textarea 是否清空：
```javascript
chatTa.value === '' // true 表示发送成功
```

## DM 模板

根据用户背景和职位要求定制，示例：

### 通用模板
```
Hi! I saw your [职位标题] post and I'm very interested.

Quick intro: [X]+ years in tech, currently [当前角色]. [核心技能匹配点].

[为什么对这个职位感兴趣的一句话]

Portfolio: [简历链接]

Happy to chat if there's a fit!
```

### AI Agent / OpenClaw 专项模板（AI agent 方向高匹配职位）
```
Hi! Saw your [AI agent / agent framework / OpenClaw] post and I'm very interested.

Quick intro: Full-stack engineer with hands-on experience building AI agent systems and automation tools. Currently working on multi-agent orchestration using OpenClaw, LangChain, and custom agent frameworks.

[技术匹配点，例如：]
- Built autonomous agents with RAG + vector DB integration
- Experience with prompt engineering and LLM orchestration
- Python + Node.js + AI-driven automation systems

Your focus on [从职位描述提取的关键词] aligns perfectly with my work on agent-based architectures.

Portfolio: https://www.self.so/danny-wang-profile
Timezone: Asia/Shanghai (UTC+8)

Happy to discuss how I can contribute!
```

### 后端/系统专项模板（Backend / Full Stack / C++ / Database / Network 方向高匹配职位）
```
Hi! Saw your [Backend / Full Stack / C++ / Database / Network] post and I'm interested.

Quick intro: Full-stack engineer with experience in backend development, system programming, and distributed architectures. Strong background in Python, Node.js, and building scalable systems.

[技术匹配点，根据职位选择：]
- Backend: Python/Node.js backend services, API design, microservices architecture
- C++: System-level programming, performance optimization, low-level development
- Database: SQL/NoSQL design, query optimization, data modeling
- Network/Telecom: Distributed systems, network protocols, telecom core network experience

Your focus on [从职位描述提取的关键词] aligns well with my technical background.

Portfolio: https://www.self.so/danny-wang-profile
Timezone: Asia/Shanghai (UTC+8)

Happy to chat if there's a fit!
```

**要点**：
- 简洁（<150 words）
- 突出与职位的匹配点：
  - AI agent 职位 → 强调 agent/orchestration/automation + OpenClaw 实战
  - 后端/系统职位 → 强调 backend/database/network + scalable systems
- 附上简历/portfolio 链接
- 不要群发模板，每条针对职位定制
- AI Agent 职位可以提及 OpenClaw 实战经验（差异化竞争力）
- C++/系统职位可以强调 system-level programming（如有相关经验）

## 常见问题

### 🚨 最高优先级：绝对不能发错人

**发错人是严重错误**，可能导致：
- 向不相关的人发送求职信息（损害个人品牌）
- 泄露求职意向给错误对象
- 浪费双方时间

**防止发错人的强制措施**：
1. **必须从目标用户的 profile 页点击 "Start Chat"**（不能用顶部导航的 "Open chat"）
2. **聊天窗口打开后，强制验证用户名**（检查窗口中是否包含目标用户名）
3. **如果验证失败，立即抛错停止，不发送任何消息**
4. **发送前再次确认聊天对象**（检查 URL 或窗口标题）

### Shadow DOM 导致 snapshot 无法使用
Reddit 大量使用 Shadow DOM（766+ shadow hosts），snapshot 拿不到 ref。
**解决**：全程用 evaluate + findInShadow 递归函数操作 DOM。

### ⚠️ 关键：必须点击正确的 "Start Chat" 链接
**顶部导航的 "Open chat" 按钮** → 打开最近的聊天记录（可能是错误的人）❌  
**Profile 页面右侧边栏的 "Start Chat" 链接** → 与当前用户开始新对话 ✅  
**解决**：查找 `<a>` 标签，innerText 精确匹配 "Start Chat"（注意大小写）。

### 必须验证聊天对象
点击 "Start Chat" 后，聊天窗口会在 Shadow DOM 中弹出（不跳转页面）。
**必须检查**聊天窗口中是否包含目标用户名。
**解决**：用 `findInShadow` 查找所有文本元素，验证是否包含目标用户名（如 `Significant_View5680`）。如果不匹配，说明聊天对象错误，必须停止并报告。

### ⚠️ 发送消息：必须用 Ctrl+Enter

Reddit 聊天输入框右侧有**飞机图标**（SVG）发送按钮，但直接点击按钮有时不触发发送。

**强制要求：在 textarea 聚焦后，派发 Ctrl+Enter 键盘事件**

```javascript
chatTa.focus();
chatTa.dispatchEvent(new KeyboardEvent('keydown', {
  key: 'Enter', code: 'Enter', keyCode: 13,
  ctrlKey: true, bubbles: true
}));
```

**❌ 错误做法**：
- 查找 Submit 按钮并 click()（有时不触发）
- 查找飞机图标按钮并 click()（有时不触发）
- 尝试其他键盘事件（只有 Ctrl+Enter 可靠）

**✅ 唯一正确做法**：Ctrl+Enter 键盘事件

### 消息填入了错误的 textarea
Reddit 页面有多个 textarea（包括 recaptcha 隐藏框）。
**解决**：用 `placeholder === 'Message'` 精确匹配聊天输入框。

### Job board bot 账号
如 u/rrmdp 这类账号只是聚合转发，私信无意义。
**识别**：profile 页全是 `📢 is [hiring]` 格式的批量帖子，无个人内容。

## 不使用 Vision

本 skill 全程使用 snapshot + evaluate 操作 DOM，**不使用 screenshot**，兼容不支持 vision 的环境。
