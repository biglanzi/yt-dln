# YouTube 下载工具

这是一个基于 `yt-dlp` 的轻量命令行工具，用来下载 YouTube 视频、音频、字幕和播放列表。

## 安装

当前环境如果已经有 `yt-dlp`，可以直接运行：

```bash
python3 ytdl.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

推荐以可编辑方式安装命令：

```bash
python -m pip install -e .
```

安装后可使用：

```bash
ytdl "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 常用命令

下载最高质量 MP4：

```bash
ytdl "https://www.youtube.com/watch?v=VIDEO_ID"
```

下载 1080p 以内视频：

```bash
ytdl -q 1080p "https://www.youtube.com/watch?v=VIDEO_ID"
```

提取 MP3：

```bash
ytdl -x --audio-format mp3 "https://www.youtube.com/watch?v=VIDEO_ID"
```

查看将要下载的视频信息：

```bash
ytdl --dry-run "https://www.youtube.com/watch?v=VIDEO_ID"
```

指定输出目录：

```bash
ytdl -o downloads/my-videos "https://www.youtube.com/watch?v=VIDEO_ID"
```

列出可用格式：

```bash
ytdl --list-formats "https://www.youtube.com/watch?v=VIDEO_ID"
```

下载整个播放列表：

```bash
ytdl --playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

只下载播放列表第 9 个条目，并跳过不可用视频：

```bash
ytdl --playlist --playlist-items 9 --ignore-errors "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

下载播放列表第 12 到第 99 个条目：

```bash
ytdl --playlist --playlist-items 12-99 "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

更保守地下载，降低触发限流的概率：

```bash
ytdl \
  --sleep-requests 0.75 \
  --sleep-interval 10 \
  --max-sleep-interval 20 \
  --concurrent-fragments 1 \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

下载字幕：

```bash
ytdl --subtitles --auto-subtitles --subtitle-langs zh-Hans,zh,en "https://www.youtube.com/watch?v=VIDEO_ID"
```

需要登录态时使用浏览器 cookies：

```bash
ytdl --cookies-from-browser chrome "https://www.youtube.com/watch?v=VIDEO_ID"
```

如果当前 Python 环境的 `bin/` 目录里存在 `deno`，工具会自动把它作为 YouTube JavaScript runtime 传给 `yt-dlp`。也可以手动指定：

```bash
ytdl --js-runtime-path ~/.local/bin/deno "https://www.youtube.com/watch?v=VIDEO_ID"
```

部分视频还需要 YouTube JS challenge solver。工具默认允许 `yt-dlp` 从 GitHub 获取该组件；需要关闭时加 `--no-remote-ejs`：

```bash
ytdl --no-remote-ejs "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 依赖说明

- 视频下载依赖 `yt-dlp>=2026.6.9`。
- 部分 YouTube 视频提取需要 JavaScript runtime，建议安装 `deno` 并确保命令可被当前环境找到。
- 默认会允许 `yt-dlp` 从 GitHub 获取 YouTube challenge solver 组件，可用 `--no-remote-ejs` 关闭。
- 音频提取、字幕嵌入、格式合并通常需要系统已安装 `ffmpeg`。
- 下载文件默认保存到 `downloads/`。

## 测试

```bash
python -m unittest discover
```

## 下载指定播放列表剩余集数

仓库提供了一个脚本用于下载已确认可下载的第 12 到第 99 集：

```bash
scripts/download_remaining_playlist.sh
```

脚本默认会在元数据请求之间等待 `0.75` 秒，在每个视频下载前随机等待 `10-20` 秒，并把分片并发降为 `1`，降低连续下载触发限流的概率。

可通过环境变量覆盖默认行为：

```bash
OUTPUT_DIR=downloads/labula PLAYLIST_ITEMS=12-99 SLEEP_INTERVAL=15 MAX_SLEEP_INTERVAL=30 RATE_LIMIT=4M scripts/download_remaining_playlist.sh
```

如果 `ytdl` 不在 `PATH` 里，可用 `YTDL_BIN` 指定命令路径。
