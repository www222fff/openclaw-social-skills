---
name: x-comment
description: >-
  在 X（Twitter/X.com）的推荐时间线上自动浏览并评论技术类和 BTC 相关推文。
  触发词：「去 X 时间线评论几条」「在 X 首页互动 BTC 内容」「帮我在 X 发几条技术评论」
---

# x-comment — X 时间线自动评论

> **核心原则：全自动，只评论不点赞，输入后直接发送，不询问用户确认。**

---

## 0. 环境

- 使用浏览器 profile：`openclaw`（已登录 X 账号）
- 禁止使用 screenshot（vision 未开启），所有信息通过 DOM/evaluate 获取
- 遇到图片只读 alt 文本

---

## 1. 触发条件与默认参数

| 参数 | 默认值 |
|------|--------|
| 话题 | 技术类（AI、agent、开发工具、编程）+ BTC/加密货币 |
| 条数 N | 3（用户可指定） |
| 动作 | 只评论，不点赞 |
| 语言 | 原推文中文（汉字 > 30%）→ 中文回复；其他 → 英文回复 |
| 语气 | 专业、友好、工程视角 |

---

## 2. 执行流程

### 步骤 1：打开 Home timeline

```jsonc
{
  "action": "open",
  "profile": "openclaw",
  "target": "host",
  "targetUrl": "https://x.com/home"
}
```

### 步骤 2：抓取候选推文

用 `evaluate` 执行以下脚本，获取前 15 条推文（含互动数据）：

```js
() => {
  const articles = Array.from(document.querySelectorAll('article[role="article"]')).slice(0, 15);
  return {
    ok: true,
    tweets: articles.map(a => {
      const href = a.querySelector('a[href*="/status/"]')?.href || null;
      const text = a.querySelector('div[data-testid="tweetText"]')?.innerText || '';
      const author = a.querySelector('div[data-testid="User-Name"] span')?.innerText || '';
      const replies = parseInt(a.querySelector('[data-testid="reply"]')?.getAttribute('aria-label')?.match(/\d+/)?.[0] || '0');
      const likes = parseInt(a.querySelector('[data-testid="like"]')?.getAttribute('aria-label')?.match(/\d+/)?.[0] || '0');
      const timeAgo = a.querySelector('time')?.getAttribute('datetime') || '';
      return { href, text, author, replies, likes, timeAgo };
    }).filter(t => t.href && t.text)
  };
}
```

**筛选优先级（从高到低）：**
1. 近期发布（< 2 小时优先）
2. 互动量适中（10–100 条回复，说明话题有热度但未饱和）
3. 话题相关（技术/BTC），排除纯政治、广告内容

### 步骤 3：生成评论

每条评论要求：
- 有实质内容（补充观点、提问、分享经验等），不要空话
- 全部使用英文评论，内容长度控制50个单词以内

### 步骤 4：发送评论（对每条推文循环执行）

**4a. 进入详情页**

```jsonc
{
  "action": "navigate",
  "targetId": "<page-id>",
  "url": "https://x.com/<user>/status/<id>"
}
```

**4b. 打开回复框**

用 `evaluate` 点击 `[data-testid="reply"]`，等待 `div[role="dialog"] div[role="textbox"][contenteditable="true"]` 出现。

**4c. 输入评论**

> ⚠️ 必须用 `browser act` + `type` + `slowly: true`。X 的编辑器只认真实键盘事件，用 evaluate 注入文本无法激活 Reply 按钮。

1. 用 `snapshot` 找到 textbox 的 ref：
   ```
   browser snapshot labels=false targetId=<page-id>
   ```
   找到 `textbox "Post text" [ref=eXXX]`

2. 输入评论：
   ```jsonc
   {
     "action": "act",
     "profile": "openclaw",
     "targetId": "<page-id>",
     "request": {
       "kind": "type",
       "ref": "eXXX",
       "text": "评论内容",
       "slowly": true
     }
   }
   ```

**4d. 点击发送**

```js
(() => {
  const dialog = document.querySelector('div[role="dialog"]');
  for (const btn of dialog?.querySelectorAll('button') || []) {
    if (btn.innerText?.trim() === 'Reply' && !btn.disabled) {
      btn.click();
      return 'sent';
    }
  }
  return 'button not found or disabled';
})()
```

等待 2 秒，检查对话框是否关闭（`dialogExists: false`）确认发送成功。

### 步骤 5：关闭标签页

```jsonc
{
  "action": "close",
  "targetId": "<page-id>"
}
```

---

## 3. 对用户的反馈格式

完成后只需回报一句话，例如：

> 「已成功发送 N 条评论。」
