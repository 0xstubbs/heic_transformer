import os
from PIL import Image
import pillow_heif
import click
from colorama import Fore, Style
from tqdm import tqdm
import hashlib


# Register the HEIF format
pillow_heif.register_heif_opener()


def print_intro():
    print(
        Fore.MAGENTA
        + Style.BRIGHT
        + "\n----------------------------------------------"
        + Style.RESET_ALL
    )
    print(
        Fore.CYAN
        + Style.BRIGHT
        + "\nWelcome to the HEIC Image Transformer!"
        + Style.RESET_ALL
    )
    print("This program converts HEIC images to JPEG or PNG format.\n")
    print(
        Fore.MAGENTA
        + Style.BRIGHT
        + "\n ----------------------------------------------"
        + Style.RESET_ALL
    )


def get_heic_files(src):
    try:
        return [
            f for f in os.listdir(src) if f.endswith(".HEIC") or f.endswith(".heic")
        ]
    except Exception as e:
        print(Fore.RED + f"Error reading directory: {str(e)}" + Style.RESET_ALL)
        return []


def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def remove_duplicate_files(src):
    files = [os.path.join(src, file) for file in os.listdir(src)]
    seen = {}
    for file in files:
        file_hash = hash_file(file)
        if file_hash in seen:
            os.remove(file)
            print(f"Removed duplicate file: {file}")
        else:
            seen[file_hash] = file


@click.command()
@click.option(
    "--src",
    prompt=Fore.GREEN
    + Style.BRIGHT
    + "Enter the source directory for the photos"
    + Style.RESET_ALL,
    help="The directory of HEIC files.",
)
@click.option(
    "--format",
    prompt=Fore.GREEN
    + Style.BRIGHT
    + "Output file format (jpeg, png)"
    + Style.RESET_ALL,
    help="The desired output format.",
)
def convert_heic(src, format):
    while True:
        try:
            # Validate format
            src = os.path.expanduser(src)
            if format not in ["jpeg", "png"]:
                raise ValueError(
                    Fore.RED
                    + "Invalid format. Please enter jpeg or png."
                    + Style.RESET_ALL
                )

            # Check if the provided source is a file or directory
            if os.path.isfile(src):
                raise ValueError(
                    Fore.RED
                    + "Error: The provided source is a file, not a directory."
                    + Style.RESET_ALL
                )
            elif not os.path.isdir(src):
                raise ValueError(
                    Fore.RED
                    + "Error: The provided source is not a valid directory."
                    + Style.RESET_ALL
                )

            # Get the list of .heic files
            files = get_heic_files(src)
            if not files:
                raise ValueError(
                    Fore.RED
                    + "Error: No .heic files found in the directory."
                    + Style.RESET_ALL
                )

            print(
                Fore.YELLOW
                + f"There are {len(files)} photos in the directory."
                + Style.RESET_ALL
            )
            print("Here are the first 10 photos:")
            for filename in files[:10]:
                print(filename)

            if not click.confirm(
                Fore.GREEN + "Is this the correct directory?" + Style.RESET_ALL
            ):
                continue
            # append "_converted" to the source directory path to form the destination directory path
            dst = src + "_converted"

            # create the destination directory if it doesn't exist
            if not os.path.exists(dst):
                os.makedirs(dst)

            print(
                Fore.YELLOW
                + f"Converting files from {src} to {dst} in {format} format..."
                + Style.RESET_ALL
            )

            # Create a list of all .heic files
            files = [
                f for f in os.listdir(src) if f.endswith(".HEIC") or f.endswith(".heic")
            ]

            # Create a progress bar
            with tqdm(
                total=len(files), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
            ) as pbar:
                for filename in files:
                    # construct the full file path
                    file_path = os.path.join(src, filename)

                    # read the heic image
                    heic_image = Image.open(file_path)

                    #                   # convert the heif image to a PIL image
                    #                   image = Image.frombytes(
                    #                       heic_image.mode,
                    #                       heic_image.size,
                    #                       heic_image.data,
                    #                       "raw",
                    #                       heic_image.mode,
                    #                       heic_image.stride,
                    #                   )

                    # construct the output filename
                    output_filename = os.path.splitext(filename)[0] + "." + format

                    # construct the full output file path
                    output_file_path = os.path.join(dst, output_filename)

                    # save the image in the chosen format
                    heic_image.save(output_file_path, format=format.upper())

                    # Update the progress bar
                    pbar.update(1)

            print(Fore.GREEN + "Conversion is done." + Style.RESET_ALL)
            break
        except Exception as e:
            print(Fore.RED + f"An error occurred: {str(e)}" + Style.RESET_ALL)


if __name__ == "__main__":
    print_intro()
    convert_heic()
