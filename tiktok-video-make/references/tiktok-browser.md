# TikTok Browser Automation Reference

## 打开 TikTok

```javascript
// Navigate to TikTok (use openclaw profile with proxy)
browser.open("https://www.tiktok.com", {profile: "openclaw"})
```

## 搜索用户

```javascript
// Method 1: Direct URL
browser.navigate(`https://www.tiktok.com/@${username}`, {profile: "openclaw"})

// Method 2: Search via input (if on homepage)
const input = document.querySelector('input[type="search"]');
input.value = '@username';
input.dispatchEvent(new Event('input', {bubbles: true}));
// Then trigger search button or Enter key
```

## 提取视频列表

```javascript
// Get video links with view counts
Array.from(document.querySelectorAll('a[href*="/video/"]'))
  .map(a => ({
    url: a.href,
    views: a.textContent.match(/[\d.]+[KMB]?/)?.[0] || '0'
  }))
```

## 常见 DOM 结构

- 搜索框：`input[type="search"]` 或 `input[placeholder*="Search"]`
- 视频链接：`a[href*="/video/"]`
- 用户主页：`https://www.tiktok.com/@用户名`
- 播放量文本：通常包含在视频卡片内的文本节点

## 注意事项

- TikTok 国际版首次加载可能显示登录提示，等待或刷新页面
- 用 `evaluate` 执行 JS，不要依赖 `snapshot`（当前环境 snapshot 返回空）
- 播放量格式：`45.5M`、`1.3K` 等（需要解析）
