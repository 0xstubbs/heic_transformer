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
git clone https://github.com/0xstubbs/heic-image-transformer.git
```
### Conda

If you are using conda create a new environments using:

```bash
conda env create -f environment.yml
```

Or update the environment using:

```bash
conda env update -f environment.yml
```

### venv

Create and activate a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

## Useage 

### To convert HEIC photos in a 'Photos' directory:

```bash
conda env create -f environment.yml
conda activate heic_transformer

python convert_heic.py
```

This starts the CLI tool and you will be prompted to enter the source directory:
"""
----------------------------------------------

Welcome to the HEIC Image Transformer!
This program converts HEIC images to JPEG or PNG format.

 ----------------------------------------------
Enter the the source directory for the photos:
"""

## Contribution

See Contributing.md for current list of #TODOs
