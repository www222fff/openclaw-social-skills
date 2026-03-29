# 自动化流程实现指南

## 架构

```
auto_pipeline.py (框架)
    ↓
OpenClaw Agent (执行)
    ↓
1. 浏览器获取候选视频
2. 过滤已下载视频
3. 下载最高播放量音频
4. 随机选择本地视频
5. 合并音视频
6. 上传到 Google Drive
7. 更新历史记录
```

## Agent 执行步骤

### Step 1: 获取候选视频

```python
# 运行框架脚本获取配置
result = subprocess.run(["python3", "scripts/auto_pipeline.py"], capture_output=True)
config = json.loads(result.stdout)
# config = {
#     "video": "/path/to/video2.mp4",
#     "accounts": ["motivationversum", "truthful_motivation"],
#     "downloaded_ids": ["7355634606177094945", ...],
#     "history_file": "/path/to/.download_history.json"
# }
```

### Step 2: 浏览器抓取

对每个账号：

```javascript
// 1. 打开账号主页
browser.navigate(`https://www.tiktok.com/@${account}`, {profile: "openclaw"})

// 2. 提取视频列表（播放量 + URL）
videos = evaluate(`
  Array.from(document.querySelectorAll('a[href*="/video/"]')).map(a => {
    const viewText = a.textContent.match(/([\\d.]+)([KMB]?)/);
    const views = viewText ? parseViews(viewText[1], viewText[2]) : 0;
    const videoId = a.href.split('/video/')[1].split('?')[0];
    return {url: a.href, views, videoId};
  }).sort((a,b) => b.views - a.views)
`)

// 3. 过滤已下载
candidates = videos.filter(v => !downloaded_ids.includes(v.videoId))

// 4. 取top 3
top = candidates.slice(0, 3)
```

**parseViews 函数**：
```javascript
function parseViews(num, unit) {
  const multipliers = {K: 1000, M: 1000000, B: 1000000000};
  return parseFloat(num) * (multipliers[unit] || 1);
}
```

### Step 3: 选择并下载

```python
# 从所有账号的候选中选择播放量最高的
all_candidates = []  # 汇总所有账号的top3
selected = max(all_candidates, key=lambda x: x['views'])

# 下载音频
subprocess.run([
    "bash", "scripts/download_tiktok_audio.sh",
    selected['url'],
    f"{selected['videoId']}_audio"
])
```

### Step 4: 合并视频

```python
audio_file = f"{WORKSPACE}/20260316_HHMM_{selected['videoId']}_audio.mp3"
output_name = f"{selected['videoId']}_final"

subprocess.run([
    "bash", "scripts/merge_audio_video.sh",
    config['video'],
    audio_file,
    output_name
])
```

### Step 5: 上传

```python
final_video = f"{WORKSPACE}/20260316_HHMM_{output_name}.mp4"
subprocess.run([
    "bash", "scripts/upload_to_gdrive.sh",
    final_video
])
```

### Step 6: 更新历史

```python
import json

with open(config['history_file'], 'r') as f:
    history = json.load(f)

history['downloaded_ids'].append(selected['videoId'])
history['last_update'] = datetime.now().isoformat()

with open(config['history_file'], 'w') as f:
    json.dump(history, f, indent=2)
```

## 播放量解析

TikTok 播放量格式：`45.5M`, `1.3K`, `803`

**转换规则**：
- `K` = ×1,000
- `M` = ×1,000,000
- `B` = ×1,000,000,000

**示例**：
- `45.5M` → 45,500,000
- `1.3K` → 1,300
- `803` → 803

## 错误处理

### 浏览器超时
- 等待页面加载（sleep 3-5秒）
- 刷新页面重试

### 无候选视频
- 所有视频都已下载 → 清空部分历史或扩展账号列表
- 账号无视频 → 跳过该账号

### 下载失败
- 记录失败，继续下一个候选
- 不更新历史文件

## 示例：完整流程

```bash
# 1. 准备视频文件
cp video1.mp4 ~/.openclaw/workspace/downloads/videos/

# 2. OpenClaw Agent 调用
# Agent: "执行 tiktok-video-make 自动化流程"

# 内部执行：
python3 scripts/auto_pipeline.py  # 获取配置
# → 随机选择 video1.mp4
# → 浏览器抓取 motivationversum 和 truthful_motivation
# → 过滤已下载，选播放量最高
# → 下载音频
# → 合并视频
# → 上传到 Google Drive
# → 更新历史

# 3. 结果
# Google Drive: 20260316_1425_7123456789_final.mp4
```

## 定时任务

使用 OpenClaw cron 每天自动运行：

```json
{
  "name": "Daily TikTok Video",
  "schedule": {"kind": "cron", "expr": "0 10 * * *", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "执行 tiktok-video-make 自动化流程",
    "timeoutSeconds": 300
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "2110348664"
  }
}
```

每天上午10点自动生成一个视频并通知到 Telegram。
