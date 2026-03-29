# Reddit Job Hunter Skill 优化建议

## 当前流程分析

### 痛点 1：搜索效率低
**问题**：
- 每次只搜索一个板块，需要手动切换
- 没有去重机制，可能重复看到同一个帖子
- 没有状态跟踪，不知道哪些职位已经联系过

**优化方案**：
1. **批量搜索**：一次任务自动遍历 4 个板块（r/DeveloperJobs, r/forhire, r/AIJobs, r/remotejs）
2. **去重机制**：用 Set 存储 href，避免重复处理
3. **状态文件**：记录已联系过的用户，避免重复发送

### 痛点 2：筛选职位需要人工判断
**问题**：
- 需要逐个打开帖子查看详情
- bot 账号识别需要进入 profile 页
- 匹配度评分是文字描述，没有自动化

**优化方案**：
1. **一次抓取多个帖子**：批量提取标题和发帖人
2. **bot 检测优化**：
   - 黑名单：维护已知 bot 账号列表（u/rrmdp, u/Varqu 等）
   - 关键词过滤：标题包含 "devitjobs.com" / "📢" 等直接跳过
3. **自动评分**：
   - 标题包含 AI agent 关键词 → 高匹配
   - 标题包含 Python/Node.js/fullstack → 中匹配
   - 其他 → 低匹配

### 痛点 3：验证步骤冗长
**问题**：
- 验证聊天对象需要 2-3 秒等待
- `findInShadow` 递归查找整个文档（性能差）

**优化方案**：
1. **减少等待时间**：从 2 秒降到 1 秒（聊天窗口通常 <1 秒加载完成）
2. **优化查找范围**：只查找包含用户名的元素（如 `[data-author]`），不需要全文检索

### 痛点 4：没有批量处理能力
**问题**：
- 用户要求"DM 2 条"，但实际只能一次处理一个
- 找到多个匹配职位时，需要手动选择

**优化方案**：
1. **目标数量参数**：`targetCount=2` 自动发送 2 条
2. **优先级排序**：高匹配职位优先发送
3. **失败重试**：一个职位失败不影响后续职位

### 痛点 5：DM 内容重复工作
**问题**：
- 每次都要从头生成 DM 内容
- 没有针对不同职位的模板切换逻辑

**优化方案**：
1. **模板选择逻辑**：
   - 标题包含 "AI agent" → 使用 AI Agent 专项模板
   - 其他 → 使用通用模板
2. **动态字段提取**：
   - 从职位标题提取关键词（如 "Python", "React", "RAG"）
   - 自动填充到模板的 [技术匹配点] 部分

## 推荐优化方案（按优先级）

### 优先级 1：状态文件跟踪（避免重复发送）
```javascript
// ~/.openclaw/workspace/skills/reddit-job-hunter/sent-state.json
{
  "sentUsers": [
    "Dense-Try-7798",
    "Neither-Mushroom-721"
  ],
  "lastRun": 1742260800000
}
```

### 优先级 2：批量搜索 + 去重
```javascript
const boards = ['DeveloperJobs', 'forhire', 'AIJobs', 'remotejs'];
const allPosts = new Set();

for (const board of boards) {
  const posts = await searchBoard(board, 'hiring AI agent');
  posts.forEach(p => allPosts.add(p.href));
}

// 去重后批量处理
const uniquePosts = [...allPosts];
```

### 优先级 3：Bot 黑名单
```javascript
const BOT_ACCOUNTS = ['rrmdp', 'Varqu', 'devitjobs'];
const BOT_KEYWORDS = ['devitjobs.com', '📢', 'Apply Now'];

function isBot(author, title) {
  return BOT_ACCOUNTS.includes(author) || 
         BOT_KEYWORDS.some(kw => title.includes(kw));
}
```

### 优先级 4：自动模板选择
```javascript
function selectTemplate(title, content) {
  const aiKeywords = ['AI agent', 'agent framework', 'OpenClaw', 'LangChain', 'RAG'];
  const isAIJob = aiKeywords.some(kw => title.includes(kw) || content.includes(kw));
  
  return isAIJob ? AI_AGENT_TEMPLATE : GENERAL_TEMPLATE;
}
```

### 优先级 5：批量发送
```javascript
async function sendBatch(posts, targetCount = 2) {
  const results = [];
  
  for (let i = 0; i < Math.min(posts.length, targetCount); i++) {
    try {
      await sendDM(posts[i]);
      results.push({ success: true, user: posts[i].author });
    } catch (err) {
      results.push({ success: false, user: posts[i].author, error: err.message });
    }
  }
  
  return results;
}
```

## 不推荐的优化（会增加复杂度）

❌ **自动回复检测**：Reddit 不提供 API，需要轮询检查，成本高  
❌ **职位详情 AI 分析**：LLM 调用成本高，标题筛选已足够  
❌ **多账号轮换**：违反 Reddit 规则，风险大  

## 总结

**立即可做的优化**（不改核心流程）：
1. ✅ Bot 黑名单（5 分钟）
2. ✅ 状态文件跟踪（10 分钟）
3. ✅ 自动模板选择（5 分钟）

**需要重构的优化**（改核心流程）：
4. 批量搜索 + 去重（30 分钟）
5. 批量发送（20 分钟）

**ROI 最高的优化**：状态文件 + Bot 黑名单（避免无效 DM）
