import unittest
from pathlib import Path

from ytdl_tool.downloader import DownloadRequest, build_ydl_options, summarize_info
from ytdl_tool.downloader import _version_is_supported


class BuildOptionsTest(unittest.TestCase):
    def test_default_video_options(self):
        request = DownloadRequest(urls=["https://youtu.be/example"], output_dir=Path("downloads"))

        options = build_ydl_options(request)

        self.assertIn("bv*[ext=mp4]+ba[ext=m4a]", options["format"])
        self.assertEqual(options["outtmpl"], "downloads/%(title).200B [%(id)s].%(ext)s")
        self.assertTrue(options["noplaylist"])
        self.assertEqual(options["merge_output_format"], "mp4")

    def test_quality_caps_height(self):
        request = DownloadRequest(
            urls=["https://youtu.be/example"],
            output_dir=Path("out"),
            quality="720p",
        )

        options = build_ydl_options(request)

        self.assertIn("height<=720", options["format"])

    def test_audio_only_adds_postprocessor(self):
        request = DownloadRequest(
            urls=["https://youtu.be/example"],
            output_dir=Path("out"),
            audio_only=True,
            audio_format="m4a",
        )

        options = build_ydl_options(request)

        self.assertEqual(options["format"], "bestaudio/best")
        self.assertEqual(options["postprocessors"][0]["key"], "FFmpegExtractAudio")
        self.assertEqual(options["postprocessors"][0]["preferredcodec"], "m4a")

    def test_cookies_from_browser_is_normalized(self):
        request = DownloadRequest(
            urls=["https://youtu.be/example"],
            output_dir=Path("out"),
            cookies_from_browser="firefox:default-release",
        )

        options = build_ydl_options(request)

        self.assertEqual(options["cookiesfrombrowser"], ("firefox", "default-release", None, None))

    def test_js_runtime_path_is_configured(self):
        request = DownloadRequest(
            urls=["https://youtu.be/example"],
            output_dir=Path("out"),
            js_runtime_path=Path(".deno/bin/deno"),
        )

        options = build_ydl_options(request)

        self.assertEqual(options["js_runtimes"], {"deno": {"path": ".deno/bin/deno"}})

    def test_remote_ejs_is_enabled_by_default(self):
        request = DownloadRequest(urls=["https://youtu.be/example"], output_dir=Path("out"))

        options = build_ydl_options(request)

        self.assertEqual(options["remote_components"], {"ejs:github"})

    def test_remote_ejs_can_be_disabled(self):
        request = DownloadRequest(
            urls=["https://youtu.be/example"],
            output_dir=Path("out"),
            allow_remote_ejs=False,
        )

        options = build_ydl_options(request)

        self.assertNotIn("remote_components", options)

    def test_playlist_controls(self):
        request = DownloadRequest(
            urls=["https://www.youtube.com/playlist?list=example"],
            output_dir=Path("out"),
            playlist=True,
            playlist_items="7-9",
            ignore_errors=True,
        )

        options = build_ydl_options(request)

        self.assertFalse(options["noplaylist"])
        self.assertEqual(options["playlist_items"], "7-9")
        self.assertTrue(options["ignoreerrors"])

    def test_dry_run_skips_download(self):
        request = DownloadRequest(urls=["https://youtu.be/example"], output_dir=Path("out"), dry_run=True)

        options = build_ydl_options(request)

        self.assertTrue(options["simulate"])
        self.assertTrue(options["skip_download"])

    def test_rate_limit_is_converted_to_bytes(self):
        request = DownloadRequest(
            urls=["https://youtu.be/example"],
            output_dir=Path("out"),
            rate_limit="1.5M",
        )

        options = build_ydl_options(request)

        self.assertEqual(options["ratelimit"], 1572864)

    def test_summarize_single_info(self):
        lines = summarize_info(
            {
                "title": "Demo",
                "duration_string": "1:23",
                "uploader": "Uploader",
                "webpage_url": "https://example.test/video",
            }
        )

        self.assertEqual(lines, ["- Demo | 1:23 | Uploader | https://example.test/video"])

    def test_version_check(self):
        self.assertFalse(_version_is_supported("2024.04.09"))
        self.assertTrue(_version_is_supported("2026.6.9"))
        self.assertTrue(_version_is_supported("2026.7.1"))


if __name__ == "__main__":
    unittest.main()
