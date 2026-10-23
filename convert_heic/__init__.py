import hashlib
from pathlib import Path

import click
from colorama import Fore, Style
from PIL import Image
import pillow_heif
from prompt_toolkit import prompt as terminal_prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style as PromptStyle
from tqdm import tqdm


# Register the HEIF format
pillow_heif.register_heif_opener()

VALID_FORMATS = ("jpeg", "png")


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


def get_path_completions(text):
    if text.endswith("/"):
        directory = Path(text).expanduser()
        prefix = ""
    else:
        expanded_path = Path(text).expanduser() if text else Path()
        directory = expanded_path.parent
        prefix = expanded_path.name

    try:
        matches = sorted(
            (entry for entry in directory.iterdir() if entry.name.startswith(prefix)),
            key=lambda entry: (entry.name.casefold(), entry.name),
        )
    except (OSError, ValueError):
        return []

    home = Path.home()
    completions = []

    for match in matches:
        completion = str(match)
        if text.startswith("~"):
            try:
                completion = f"~/{match.relative_to(home)}"
            except ValueError:
                pass
        if match.is_dir():
            completion += "/"
        completions.append(completion)

    return completions


class SourcePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        for completion in get_path_completions(text):
            is_directory = completion.endswith("/")
            display = Path(completion.rstrip("/")).name
            if is_directory:
                display += "/"
            yield Completion(
                completion,
                start_position=-len(text),
                display=display,
                display_meta="directory" if is_directory else "file",
            )


def prompt_for_source():
    return terminal_prompt(
        FormattedText(
            [
                (
                    "class:source-prompt",
                    "Enter a HEIC file or source directory: ",
                )
            ]
        ),
        completer=SourcePathCompleter(),
        complete_style=CompleteStyle.MULTI_COLUMN,
        complete_while_typing=False,
        style=PromptStyle.from_dict({"source-prompt": "ansigreen bold"}),
    )


def normalize_source_dir(src):
    src_path = Path(src).expanduser().resolve()
    if not src_path.is_file() and not src_path.is_dir():
        raise ValueError("Error: The provided source is not a valid file or directory.")
    return src_path


def get_heic_files(src):
    src_path = Path(src)
    if src_path.is_file():
        return [src_path] if src_path.suffix.lower() == ".heic" else []
    return sorted(
        path
        for path in src_path.iterdir()
        if path.is_file() and path.suffix.lower() == ".heic"
    )


def build_destination_dir(src, dst=None):
    src_path = Path(src).expanduser().resolve()
    if dst:
        return Path(dst).expanduser().resolve()
    if src_path.is_file():
        return src_path.parent / f"{src_path.stem}_converted"
    return src_path.parent / f"{src_path.name}_converted"


def hash_file(file_path, chunk_size=1024 * 1024):
    hasher = hashlib.md5()
    with open(file_path, "rb") as file_handle:
        while chunk := file_handle.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def remove_duplicate_files(src):
    files = [path for path in Path(src).iterdir() if path.is_file()]
    seen = {}
    for file_path in files:
        file_hash = hash_file(file_path)
        if file_hash in seen:
            file_path.unlink()
            print(f"Removed duplicate file: {file_path}")
        else:
            seen[file_hash] = file_path


def convert_image_file(file_path, destination_dir, output_format):
    output_file_path = Path(destination_dir) / f"{Path(file_path).stem}.{output_format}"

    with Image.open(file_path) as image:
        save_image = image
        if output_format == "jpeg" and image.mode != "RGB":
            save_image = image.convert("RGB")
        save_image.save(output_file_path, format=output_format.upper())

    return output_file_path


def convert_directory(src, output_format, dst=None):
    normalized_format = output_format.lower()
    if normalized_format not in VALID_FORMATS:
        raise ValueError("Invalid format. Please enter jpeg or png.")

    src_path = normalize_source_dir(src)
    files = get_heic_files(src_path)
    if not files:
        raise ValueError("Error: No .heic files found in the directory.")

    destination_dir = build_destination_dir(src_path, dst)
    destination_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    failed = 0
    errors = []

    with tqdm(total=len(files), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        for file_path in files:
            try:
                convert_image_file(file_path, destination_dir, normalized_format)
                converted += 1
            except Exception as exc:
                failed += 1
                errors.append((file_path.name, str(exc)))
            finally:
                pbar.update(1)

    return {
        "source": src_path,
        "destination": destination_dir,
        "converted": converted,
        "failed": failed,
        "errors": errors,
        "total": len(files),
    }


@click.command()
@click.option(
    "--src",
    help="A HEIC file or directory of HEIC files.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(VALID_FORMATS, case_sensitive=False),
    help="The desired output format.",
)
@click.option(
    "--dst",
    help="Optional output directory. Defaults to a sibling '<source>_converted' folder.",
)
def convert_heic(src, output_format, dst):
    try:
        if src is None:
            src = prompt_for_source()
        if output_format is None:
            output_format = click.prompt(
                Fore.GREEN
                + Style.BRIGHT
                + "Output file format (jpeg, png)"
                + Style.RESET_ALL,
                type=click.Choice(VALID_FORMATS, case_sensitive=False),
            )
        src_path = normalize_source_dir(src)
        files = get_heic_files(src_path)
        if not files:
            raise ValueError("Error: No .heic files found in the directory.")

        print(
            Fore.YELLOW
            + f"There are {len(files)} photos in the directory."
            + Style.RESET_ALL
        )
        print("Here are the first 10 photos:")
        for filename in files[:10]:
            print(filename.name)

        if not click.confirm(
            Fore.GREEN + "Is this the correct directory?" + Style.RESET_ALL
        ):
            raise click.Abort()

        destination_dir = build_destination_dir(src_path, dst)
        print(
            Fore.YELLOW
            + f"Converting files from {src_path} to {destination_dir} in {output_format.lower()} format..."
            + Style.RESET_ALL
        )

        result = convert_directory(src_path, output_format, dst)

        print(
            Fore.GREEN
            + f"Conversion is done. Saved {result['converted']} of {result['total']} files to {result['destination']}."
            + Style.RESET_ALL
        )

        if result["failed"]:
            print(
                Fore.RED
                + f"{result['failed']} files failed to convert:"
                + Style.RESET_ALL
            )
            for filename, error_message in result["errors"]:
                print(Fore.RED + f"- {filename}: {error_message}" + Style.RESET_ALL)
    except click.Abort:
        print(Fore.YELLOW + "Conversion cancelled." + Style.RESET_ALL)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    print_intro()
    convert_heic()
