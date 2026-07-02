from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .downloader import DEFAULT_TEMPLATE, DownloadRequest, run_download


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ytdl",
        description="Download YouTube videos or audio with a small yt-dlp based CLI.",
    )
    parser.add_argument("urls", nargs="+", help="YouTube video, short, channel, or playlist URL")
    parser.add_argument("-o", "--output-dir", default="downloads", type=Path, help="download directory")
    parser.add_argument(
        "--filename-template",
        default=DEFAULT_TEMPLATE,
        help="yt-dlp output template, relative to --output-dir",
    )
    parser.add_argument("-f", "--format", dest="format_selector", help="custom yt-dlp format selector")
    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        choices=["best", "2160p", "1440p", "1080p", "720p", "480p", "360p"],
        help="maximum video quality when --format is not set",
    )

    media = parser.add_argument_group("media")
    media.add_argument("-x", "--audio-only", action="store_true", help="extract audio instead of video")
    media.add_argument(
        "--audio-format",
        default="mp3",
        choices=["mp3", "m4a", "opus", "wav", "flac"],
        help="audio format used with --audio-only",
    )
    media.add_argument("--audio-quality", default="0", help="FFmpeg audio quality, 0 is best for mp3")
    media.add_argument("--merge-output-format", default="mp4", choices=["mp4", "mkv", "webm"])
    media.add_argument("--thumbnail", action="store_true", help="download thumbnail")

    playlist = parser.add_argument_group("playlist")
    playlist.add_argument("--playlist", action="store_true", help="download entire playlist when URL contains one")
    playlist.add_argument(
        "--playlist-items",
        help="playlist item range accepted by yt-dlp, for example 1,3,7-10",
    )

    subtitles = parser.add_argument_group("subtitles")
    subtitles.add_argument("--subtitles", action="store_true", help="download manually provided subtitles")
    subtitles.add_argument("--auto-subtitles", action="store_true", help="download auto-generated subtitles")
    subtitles.add_argument("--subtitle-langs", default="zh-Hans,zh,en", help="comma separated subtitle languages")
    subtitles.add_argument("--embed-subtitles", action="store_true", help="embed subtitles into the media file")

    network = parser.add_argument_group("network/auth")
    network.add_argument("--cookies", type=Path, help="cookies.txt file for login-required videos")
    network.add_argument(
        "--cookies-from-browser",
        help="browser cookie source, for example chrome, chromium, firefox, or firefox:profile",
    )
    network.add_argument("--js-runtime-path", type=Path, help="path to deno, node, bun, or quickjs runtime")
    network.add_argument(
        "--allow-remote-ejs",
        action="store_true",
        default=True,
        help="allow yt-dlp to fetch YouTube JS challenge solver components from GitHub (default)",
    )
    network.add_argument(
        "--no-remote-ejs",
        dest="allow_remote_ejs",
        action="store_false",
        help="disable fetching YouTube JS challenge solver components from GitHub",
    )
    network.add_argument("--proxy", help="proxy URL, for example socks5://127.0.0.1:1080")
    network.add_argument("--rate-limit", help="download rate limit accepted by yt-dlp, for example 2M")
    network.add_argument("--retries", default=10, type=int)
    network.add_argument("--fragment-retries", default=10, type=int)
    network.add_argument("--concurrent-fragments", default=4, type=int)

    behavior = parser.add_argument_group("behavior")
    behavior.add_argument("--dry-run", action="store_true", help="extract and print video info without downloading")
    behavior.add_argument("--list-formats", action="store_true", help="list available formats and exit")
    behavior.add_argument("--ignore-errors", action="store_true", help="skip unavailable playlist entries")
    behavior.add_argument("--no-continue", dest="continue_download", action="store_false", help="do not resume partial files")
    behavior.add_argument("--overwrite", dest="no_overwrites", action="store_false", help="overwrite existing files")
    behavior.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    return parser


def request_from_args(args: argparse.Namespace) -> DownloadRequest:
    return DownloadRequest(
        urls=args.urls,
        output_dir=args.output_dir,
        filename_template=args.filename_template,
        format_selector=args.format_selector,
        quality=args.quality,
        audio_only=args.audio_only,
        audio_format=args.audio_format,
        audio_quality=args.audio_quality,
        playlist=args.playlist,
        playlist_items=args.playlist_items,
        subtitles=args.subtitles,
        auto_subtitles=args.auto_subtitles,
        subtitle_langs=args.subtitle_langs,
        embed_subtitles=args.embed_subtitles,
        thumbnail=args.thumbnail,
        cookies=args.cookies,
        cookies_from_browser=args.cookies_from_browser,
        js_runtime_path=args.js_runtime_path,
        allow_remote_ejs=args.allow_remote_ejs,
        proxy=args.proxy,
        rate_limit=args.rate_limit,
        retries=args.retries,
        fragment_retries=args.fragment_retries,
        concurrent_fragments=args.concurrent_fragments,
        merge_output_format=args.merge_output_format,
        dry_run=args.dry_run,
        list_formats=args.list_formats,
        ignore_errors=args.ignore_errors,
        continue_download=args.continue_download,
        no_overwrites=args.no_overwrites,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_download(request_from_args(args))
