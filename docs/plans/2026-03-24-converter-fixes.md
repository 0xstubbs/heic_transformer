# Converter Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make HEIC conversions save to a predictable destination, survive per-file failures, and expose a runnable CLI that actually executes the converter.

**Architecture:** Refactor `convert_heic.py` into small helpers that separate validation, destination resolution, and per-file conversion from Click prompting. Keep the Click command as the user-facing interface, but move the core behavior into importable functions so it can be regression-tested with `unittest` and `click.testing`.

**Tech Stack:** Python 3.13, Click, Pillow, pillow-heif, pathlib, unittest

---

### Task 1: Add regression tests for path resolution and conversion behavior

**Files:**
- Create: `tests/test_convert_heic.py`
- Modify: `convert_heic.py`

**Step 1: Write the failing test**

```python
def test_default_output_directory_uses_source_name(self):
    src = self.temp_path / "photos"
    src.mkdir()
    self.assertEqual(
        convert_heic.build_destination_dir(src, None),
        src.parent / "photos_converted",
    )
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_convert_heic -v`
Expected: FAIL because `build_destination_dir` does not exist yet.

**Step 3: Write minimal implementation**

```python
def build_destination_dir(src, dst=None):
    src_path = Path(src).expanduser().resolve()
    if dst is not None:
        return Path(dst).expanduser().resolve()
    return src_path.parent / f"{src_path.name}_converted"
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_convert_heic -v`
Expected: PASS for the new test.

**Step 5: Commit**

```bash
git add tests/test_convert_heic.py convert_heic.py
git commit -m "test: cover converter output path behavior"
```

### Task 2: Add regression tests for JPEG mode conversion and per-file failure isolation

**Files:**
- Modify: `tests/test_convert_heic.py`
- Modify: `convert_heic.py`

**Step 1: Write the failing test**

```python
def test_convert_directory_continues_after_file_error(self):
    results = convert_heic.convert_directory(self.src, "jpeg", self.dst)
    self.assertEqual(results["converted"], 1)
    self.assertEqual(results["failed"], 1)
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_convert_heic -v`
Expected: FAIL because the converter aborts on the first exception and does not return a summary.

**Step 3: Write minimal implementation**

```python
for filename in files:
    try:
        convert_file(...)
        converted += 1
    except Exception:
        failed += 1
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_convert_heic -v`
Expected: PASS for the failure-isolation and JPEG conversion tests.

**Step 5: Commit**

```bash
git add tests/test_convert_heic.py convert_heic.py
git commit -m "fix: isolate per-file conversion failures"
```

### Task 3: Wire the CLI entrypoint and usage docs to the real converter

**Files:**
- Modify: `main.py`
- Modify: `README.md`
- Modify: `pyproject.toml`
- Test: `tests/test_convert_heic.py`

**Step 1: Write the failing test**

```python
def test_main_delegates_to_convert_heic_cli(self):
    with patch("main.convert_heic_cli") as mock_cli:
        main.main()
    mock_cli.assert_called_once_with()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_convert_heic -v`
Expected: FAIL because `main.py` only prints a placeholder string.

**Step 3: Write minimal implementation**

```python
from convert_heic import convert_heic as convert_heic_cli

def main():
    convert_heic_cli()
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_convert_heic -v`
Expected: PASS for the entrypoint test.

**Step 5: Commit**

```bash
git add main.py README.md pyproject.toml tests/test_convert_heic.py
git commit -m "fix: expose converter cli entrypoint"
```
