# HEIC Image Transformer

HEIC Image Transformer is a Python application that converts HEIC images to JPEG or PNG format. 

## Features

- Converts HEIC images to JPEG or PNG format.
- Supports batch processing of files in a directory.
- Checks for and removes duplicate images to avoid unnecessary processing.
- Displays a progress bar for tracking the conversion process.
  
## Installation

Clone the repository to your machine:

```bash
git clone https://github.com/0xstubbs/heic_transformer.git
```

## Environment

I recommend using 'uv' for environment management.

```bash
# Install the packages and source the environment
uv sync
source .venv/bin/activate
```

## Usage

### Convert a Single HEIC File to PNG

```bash
uv run python main.py --src ~/Pictures/photo.HEIC --format png
```

A single file is written to a sibling directory named `<file-stem>_converted`.
For example, `~/Pictures/photo.HEIC` writes `~/Pictures/photo_converted/photo.png`.
Use `--dst ~/Pictures` to choose a different output directory.

### Convert All HEIC Files in a Directory to JPEG

To convert HEIC photos in a `Photos` directory, run:

```bash
uv run python main.py
```

This starts the CLI tool and you will be prompted to enter the source directory:

"""
----------------------------------------------

Welcome to the HEIC Image Transformer!
This program converts HEIC images to JPEG or PNG format.

 ----------------------------------------------
Enter the source directory for the photos:

"""

By default, converted images are written to a sibling directory named `<source>_converted`.
For example, `/Users/me/Photos` writes to `/Users/me/Photos_converted`.

You can also run it non-interactively:

```bash
uv run python main.py --src ~/Photos --format png
```
