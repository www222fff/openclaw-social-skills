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
- r/forhire（[Hiring] 标签帖子）
- r/AIJobs（AI/ML 相关职位）
- r/remotejs、r/golang（技术栈专项）
- 全站搜索：`/search/?q="hiring" "engineer"&sort=new&t=week`

**搜索示例**：
```
navigate: https://www.reddit.com/r/forhire/search/?q=hiring%20backend&sort=new&t=week
```

### 3. 筛选职位

用 evaluate 提取帖子列表：
```javascript
[...document.querySelectorAll('a[href*="/comments/"]')]
  .map(a => ({ href: a.href, text: a.innerText.slice(0, 120) }))
  .filter(p => /hiring/i.test(p.text))
```

**排除 bot 账号**：
- 检查发帖人 profile，若全是 job board 聚合帖（如 u/rrmdp）则跳过
- 优先选择：帖子有具体职位描述、发帖人有个人资料、非批量转发

### 4. 查看职位详情

导航到具体帖子，提取职位要求：
```javascript
document.body.innerText.slice(0, 2000)
```

判断是否匹配用户背景（技术栈、经验年限、remote/onsite）。

### 5. 私信招聘方

**进入用户 profile 页**：
```
navigate: https://www.reddit.com/user/<username>
```

**点击 Chat 按钮**：
```javascript
const btns = [...document.querySelectorAll('button')];
const chatBtn = btns.find(b => /open\s*chat/i.test(b.innerText));
chatBtn.click();
```

**填写消息**（Reddit 使用 Shadow DOM，需递归搜索）：
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

const textareas = findInShadow(document, 'textarea');
const chatTa = textareas.find(ta => ta.placeholder === 'Message');
chatTa.focus();
chatTa.value = "<消息内容>";
chatTa.dispatchEvent(new Event('input', { bubbles: true }));
```

**点击发送**：
```javascript
const allBtns = findInShadow(document, 'button');
const sendBtn = allBtns.find(b => b.getAttribute('aria-label') === 'Send message');
sendBtn.click();
```

### 6. 验证发送成功

检查 textarea 是否清空：
```javascript
chatTa.value === '' // true 表示发送成功
```

## DM 模板

根据用户背景和职位要求定制，示例：

```
Hi! I saw your [职位标题] post and I'm very interested.

Quick intro: [X]+ years in tech, currently [当前角色]. [核心技能匹配点].

[为什么对这个职位感兴趣的一句话]

Portfolio: [简历链接]

Happy to chat if there's a fit!
```

**要点**：
- 简洁（<150 words）
- 突出与职位的匹配点
- 附上简历/portfolio 链接
- 不要群发模板，每条针对职位定制

## 常见问题

### Shadow DOM 导致 snapshot 无法使用
Reddit 大量使用 Shadow DOM（766+ shadow hosts），snapshot 拿不到 ref。
**解决**：全程用 evaluate + findInShadow 递归函数操作 DOM。

### Chat 按钮点击无效
可能是 aria-label 不匹配或按钮在 shadow root 里。
**解决**：用文本匹配 `btns.find(b => /open\s*chat/i.test(b.innerText))`

### 消息填入了错误的 textarea
Reddit 页面有多个 textarea（包括 recaptcha 隐藏框）。
**解决**：用 `placeholder === 'Message'` 精确匹配聊天输入框。

### Job board bot 账号
如 u/rrmdp 这类账号只是聚合转发，私信无意义。
**识别**：profile 页全是 `📢 is [hiring]` 格式的批量帖子，无个人内容。

## 不使用 Vision

本 skill 全程使用 snapshot + evaluate 操作 DOM，**不使用 screenshot**，兼容不支持 vision 的环境。
