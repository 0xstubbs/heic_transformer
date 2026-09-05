import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

import convert_heic
import main


class FakeImage:
    def __init__(self, mode="RGBA"):
        self.mode = mode
        self.saved_paths = []
        self.convert_calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def convert(self, mode):
        self.convert_calls.append(mode)
        return FakeImage(mode=mode)

    def save(self, output_path, format):
        Path(output_path).write_bytes(f"{self.mode}:{format}".encode("utf-8"))
        self.saved_paths.append((Path(output_path), format))


class ConvertHeicTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.src = self.temp_path / "photos"
        self.src.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_output_directory_uses_source_name(self):
        self.assertEqual(
            convert_heic.build_destination_dir(self.src),
            self.temp_path / "photos_converted",
        )
        self.assertEqual(
            convert_heic.build_destination_dir(f"{self.src}/"),
            self.temp_path / "photos_converted",
        )

    def test_default_output_directory_uses_source_file_stem(self):
        image_file = self.src / "sample.HEIC"
        image_file.write_bytes(b"sample")

        self.assertEqual(
            convert_heic.build_destination_dir(image_file),
            self.src / "sample_converted",
        )

    def test_convert_directory_continues_after_file_error_and_saves_jpeg(self):
        good_file = self.src / "good.HEIC"
        bad_file = self.src / "bad.heic"
        good_file.write_bytes(b"good")
        bad_file.write_bytes(b"bad")

        def fake_open(path):
            if Path(path).name == "bad.heic":
                raise OSError("broken image")
            return FakeImage(mode="RGBA")

        with patch("convert_heic.Image.open", side_effect=fake_open):
            result = convert_heic.convert_directory(self.src, "jpeg")

        output_file = self.temp_path / "photos_converted" / "good.jpeg"
        self.assertEqual(result["converted"], 1)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(result["destination"], self.temp_path / "photos_converted")
        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.read_text(encoding="utf-8"), "RGB:JPEG")

    def test_main_delegates_to_convert_heic_cli(self):
        with patch("main.convert_heic_cli") as mock_cli:
            main.main()

        mock_cli.assert_called_once_with()

    def test_cli_reports_destination_directory(self):
        image_file = self.src / "sample.HEIC"
        image_file.write_bytes(b"sample")

        with patch("convert_heic.Image.open", return_value=FakeImage(mode="RGB")):
            runner = CliRunner()
            result = runner.invoke(
                convert_heic.convert_heic,
                ["--src", str(self.src), "--format", "png"],
                input="y\n",
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(str(self.temp_path / "photos_converted"), result.output)

    def test_cli_accepts_single_heic_file(self):
        image_file = self.src / "sample.HEIC"
        image_file.write_bytes(b"sample")
        destination = self.temp_path / "converted"

        with patch("convert_heic.Image.open", return_value=FakeImage(mode="RGB")):
            runner = CliRunner()
            result = runner.invoke(
                convert_heic.convert_heic,
                [
                    "--src",
                    str(image_file),
                    "--format",
                    "png",
                    "--dst",
                    str(destination),
                ],
                input="y\n",
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertTrue((destination / "sample.png").exists())
        self.assertIn("Saved 1 of 1 files", result.output)


if __name__ == "__main__":
    unittest.main()
