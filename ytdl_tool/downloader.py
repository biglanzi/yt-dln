from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_TEMPLATE = "%(title).200B [%(id)s].%(ext)s"
DEFAULT_VIDEO_FORMAT = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
MIN_YT_DLP_VERSION = "2026.6.9"
LOCAL_DENO_PATH = Path(__file__).resolve().parents[1] / ".deno" / "bin" / "deno"


@dataclass(frozen=True)
class DownloadRequest:
    urls: list[str]
    output_dir: Path
    filename_template: str = DEFAULT_TEMPLATE
    format_selector: str | None = None
    quality: str = "best"
    audio_only: bool = False
    audio_format: str = "mp3"
    audio_quality: str = "0"
    playlist: bool = False
    playlist_items: str | None = None
    subtitles: bool = False
    auto_subtitles: bool = False
    subtitle_langs: str = "zh-Hans,zh,en"
    embed_subtitles: bool = False
    thumbnail: bool = False
    cookies: Path | None = None
    cookies_from_browser: str | None = None
    js_runtime_path: Path | None = None
    allow_remote_ejs: bool = True
    proxy: str | None = None
    rate_limit: str | None = None
    sleep_requests: float | None = None
    sleep_interval: float | None = None
    max_sleep_interval: float | None = None
    retries: int = 10
    fragment_retries: int = 10
    concurrent_fragments: int = 4
    merge_output_format: str = "mp4"
    dry_run: bool = False
    list_formats: bool = False
    ignore_errors: bool = False
    continue_download: bool = True
    no_overwrites: bool = True


def _video_format_for_quality(quality: str) -> str:
    if quality == "best":
        return DEFAULT_VIDEO_FORMAT

    height = quality.removesuffix("p")
    return (
        f"bv*[height<={height}][ext=mp4]+ba[ext=m4a]/"
        f"b[height<={height}][ext=mp4]/best[height<={height}]/best"
    )


def _cookies_from_browser(value: str | None) -> tuple[str, str | None, None, None] | None:
    if not value:
        return None

    browser, _, profile = value.partition(":")
    return (browser, profile or None, None, None)


def _parse_rate_limit(value: str) -> int:
    units = {"k": 1024, "m": 1024**2, "g": 1024**3}
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError("rate limit cannot be empty")

    suffix = normalized[-1]
    if suffix in units:
        return int(float(normalized[:-1]) * units[suffix])
    return int(normalized)


def _default_js_runtime_path() -> Path | None:
    candidates = [
        Path(value)
        for value in [
            os.environ.get("YTDL_DENO_PATH"),
            str(Path(sys.executable).parent / "deno"),
            str(LOCAL_DENO_PATH),
        ]
        if value
    ]

    for path in candidates:
        if path.exists():
            return path
    return None


def _default_ffmpeg_location() -> Path | None:
    ffmpeg = Path(sys.executable).parent / "ffmpeg"
    if ffmpeg.exists():
        return ffmpeg.parent
    return None


def build_ydl_options(request: DownloadRequest) -> dict[str, Any]:
    outtmpl = str(request.output_dir / request.filename_template)

    if request.format_selector:
        format_selector = request.format_selector
    elif request.audio_only:
        format_selector = "bestaudio/best"
    else:
        format_selector = _video_format_for_quality(request.quality)

    options: dict[str, Any] = {
        "format": format_selector,
        "outtmpl": outtmpl,
        "paths": {"home": str(request.output_dir)},
        "noplaylist": not request.playlist,
        "retries": request.retries,
        "fragment_retries": request.fragment_retries,
        "concurrent_fragment_downloads": request.concurrent_fragments,
        "continuedl": request.continue_download,
        "overwrites": not request.no_overwrites,
        "ignoreerrors": request.ignore_errors,
        "merge_output_format": request.merge_output_format,
        "quiet": False,
        "no_warnings": False,
    }

    if request.dry_run:
        options.update(
            {
                "simulate": True,
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
            }
        )

    if request.list_formats:
        options.update({"listformats": True, "simulate": True, "skip_download": True})

    if request.playlist_items:
        options["playlist_items"] = request.playlist_items

    if request.audio_only:
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": request.audio_format,
                "preferredquality": request.audio_quality,
            }
        ]

    if request.subtitles:
        options.update(
            {
                "writesubtitles": True,
                "subtitleslangs": [item.strip() for item in request.subtitle_langs.split(",") if item.strip()],
            }
        )

    if request.auto_subtitles:
        options.update(
            {
                "writeautomaticsub": True,
                "subtitleslangs": [item.strip() for item in request.subtitle_langs.split(",") if item.strip()],
            }
        )

    if request.embed_subtitles:
        options["embedsubtitles"] = True

    if request.thumbnail:
        options["writethumbnail"] = True

    if request.cookies:
        options["cookiefile"] = str(request.cookies)

    cookies_from_browser = _cookies_from_browser(request.cookies_from_browser)
    if cookies_from_browser:
        options["cookiesfrombrowser"] = cookies_from_browser

    js_runtime_path = request.js_runtime_path or _default_js_runtime_path()
    if js_runtime_path:
        options["js_runtimes"] = {"deno": {"path": str(js_runtime_path)}}

    if request.allow_remote_ejs:
        options["remote_components"] = {"ejs:github"}

    ffmpeg_location = _default_ffmpeg_location()
    if ffmpeg_location:
        options["ffmpeg_location"] = str(ffmpeg_location)

    if request.proxy:
        options["proxy"] = request.proxy

    if request.rate_limit:
        options["ratelimit"] = _parse_rate_limit(request.rate_limit)

    if request.sleep_requests is not None:
        options["sleep_interval_requests"] = request.sleep_requests

    if request.sleep_interval is not None:
        options["sleep_interval"] = request.sleep_interval
        options["max_sleep_interval"] = request.max_sleep_interval or request.sleep_interval

    if request.max_sleep_interval is not None and request.sleep_interval is None:
        raise ValueError("max_sleep_interval requires sleep_interval")

    return options


def summarize_info(info: dict[str, Any]) -> list[str]:
    entries = info.get("entries")
    if entries is None:
        entries = [info]

    lines = []
    for item in entries:
        if not item:
            continue
        title = item.get("title") or "<unknown title>"
        duration = item.get("duration_string") or item.get("duration") or "?"
        uploader = item.get("uploader") or item.get("channel") or "?"
        webpage_url = item.get("webpage_url") or item.get("url") or ""
        lines.append(f"- {title} | {duration} | {uploader} | {webpage_url}")
    return lines


def _version_tuple(value: str) -> tuple[int, ...]:
    parts = []
    for part in value.replace("-", ".").split("."):
        if not part.isdigit():
            break
        parts.append(int(part))
    return tuple(parts)


def _version_is_supported(value: str) -> bool:
    return _version_tuple(value) >= _version_tuple(MIN_YT_DLP_VERSION)


def run_download(request: DownloadRequest) -> int:
    try:
        import yt_dlp
        from yt_dlp import DownloadError, YoutubeDL
    except ModuleNotFoundError:
        print("缺少依赖 yt-dlp。请先运行：python3 -m pip install -e .")
        return 2

    current_version = getattr(yt_dlp.version, "__version__", "0")
    if not _version_is_supported(current_version):
        print(
            f"当前 yt-dlp 版本为 {current_version}，本工具要求至少 {MIN_YT_DLP_VERSION}。"
            "请运行：python3 -m pip install -U yt-dlp"
        )
        return 2

    request.output_dir.mkdir(parents=True, exist_ok=True)
    options = build_ydl_options(request)

    try:
        with YoutubeDL(options) as ydl:
            if request.dry_run:
                for url in request.urls:
                    info = ydl.extract_info(url, download=False)
                    print("\n".join(summarize_info(info)))
                return 0

            if request.list_formats:
                for url in request.urls:
                    ydl.extract_info(url, download=False)
                return 0

            ydl.download(request.urls)
            return 0
    except DownloadError as exc:
        print(f"下载失败：{exc}")
        return 1
