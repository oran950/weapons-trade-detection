"""Tests for FileManager I/O helpers."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.utils.file_manager import FileManager


class TestFileManager:
    def test_creates_directories(self, tmp_path):
        fm = FileManager(str(tmp_path / "data"))
        assert fm.raw_dir.exists()
        assert fm.analyzed_dir.exists()
        assert fm.reports_dir.exists()

    def test_save_and_load_json(self, tmp_path):
        fm = FileManager(str(tmp_path / "data"))
        path = fm.save_json({"a": 1, "nested": {"b": 2}}, "sample", directory="raw")
        assert path.endswith("sample.json")
        loaded = fm.load_json("sample", directory="raw")
        assert loaded == {"a": 1, "nested": {"b": 2}}

    def test_load_missing_json(self, tmp_path):
        fm = FileManager(str(tmp_path / "data"))
        assert fm.load_json("missing") is None

    def test_save_empty_csv(self, tmp_path):
        fm = FileManager(str(tmp_path / "data"))
        path = fm.save_csv([], "empty", directory="analyzed")
        assert os.path.exists(path)
        assert os.path.getsize(path) == 0

    def test_save_csv_flattens_nested(self, tmp_path):
        fm = FileManager(str(tmp_path / "data"))
        path = fm.save_csv(
            [{"id": 1, "meta": {"score": 0.9}, "tags": ["a", "b"]}],
            "posts",
            directory="raw",
        )
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "meta_score" in content
        assert "tags" in content

    def test_list_files_and_info(self, tmp_path):
        fm = FileManager(str(tmp_path / "data"))
        fm.save_json({"x": 1}, "one", directory="reports")
        files = fm.list_files(directory="reports", extension="json")
        assert "one.json" in files
        info = fm.get_file_info("one.json", directory="reports")
        assert info is not None
        assert info["filename"] == "one.json"
        assert info["size_bytes"] > 0

    def test_generate_filename_short_and_long_sources(self, tmp_path):
        fm = FileManager(str(tmp_path / "data"))
        short = fm.generate_filename("raw", ["guns", "news"], "week")
        assert short.startswith("raw_guns_news_week_")
        long = fm.generate_filename("raw", ["a", "b", "c", "d", "e"], "day")
        assert "_and_2_more_day_" in long
