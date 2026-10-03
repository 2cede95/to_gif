from yt_dlp import YoutubeDL, utils
import ffmpeg

from tempfile import NamedTemporaryFile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from shutil import get_terminal_size
from sys import exit

FILE_INDEX_LIMIT = 1000 # used in unique_output_path
DEFAULT_FILE_NAME = "out.gif"

# Higher numbers take up more disk space
GIF_RESOLUTION_PX = 480
GIF_FPS = 15


parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
    prog="to_gif.py",
    description="Use yt_dlp and ffmpeg to attempt to convert arbitrary media to .gif format.",
)

parser.add_argument(
    '-o',
    "--output_path",
    type=Path,
    default=Path(".") / DEFAULT_FILE_NAME,
    help="Where to store the output gif.",
)

filetype_parser = parser.add_mutually_exclusive_group()

filetype_parser.add_argument(
    '-l',
    "--link",
    type=str,
    default=None,
    help="Convert a link to media into a .gif file.",
)

filetype_parser.add_argument(
    '-f',
    "--file",
    type=Path,
    default=None,
    help="Convert media file to a .gif file."
)


def download_media_and_process(url: str) -> bytes:

    with NamedTemporaryFile(suffix=".mp4") as f:
        opts = {
            "outtmpl": f.name,
            "format": "bv[height<=720]/bv",
        }

    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])

    except (utils.DownloadError, utils.DownloadCancelled):
        message = f"Error occurred during download. See above logs for details. (Exit status 1)"

        print('\n', end='') 
        print_big_terminal_message(message, delim='!')

        exit(1)

    gif = process_to_gif(Path(f.name))

    return gif

    
def process_to_gif(path: Path) -> bytes:

    try:
        gif, _ = (
                ffmpeg.input(path).output(
                    "pipe:",
                    format="gif",
                    vf=f"fps={GIF_FPS},scale={GIF_RESOLUTION_PX}:-1:flags=lanczos",
                ).run(capture_stdout=True, capture_stderr=True)
            )
    except ffmpeg.Error as e:

            message = f"{e.stderr.decode("utf-8", errors="replace")}"
            print_big_terminal_message(message, delim='!', close = False)

            message = f"Error in FFmpeg processing. See above logs for details. (Exit status 1)"
            print_big_terminal_message(message, delim='!', open = False)

            exit(1)

    return gif  


def print_big_terminal_message(message: str, delim: str = '*', open: bool = True, close: bool = True):
        
    terminal_width = get_terminal_size().columns
    
    if open: 
        print(terminal_width*delim + '\n')

    print((terminal_width - len(message))//2 * ' ' + message)
    
    if close: 
        print(terminal_width*delim, end='')


def write_gif_to_disk(gif: bytes, path: Path) -> None:

    path.write_bytes(gif)

    message = f"Success! \"{path}\" written to disk at \"{path.resolve()}\"."
    print_big_terminal_message(message)


def check_output_file_path_validity(path: Path) -> Path:

    if path.suffix == ".gif":
        return path
    else:
        return path.with_suffix(".gif")


def unique_output_path(path: Path) -> Path:
    
    if not path.exists():
        return path

    for i in range(2, FILE_INDEX_LIMIT):
        buffer_path = path.with_stem(f"{path.stem} ({i})")
        
        if not buffer_path.exists():
            return buffer_path
        
        i+=1

    return path.with_stem(f"{path.stem} ({FILE_INDEX_LIMIT})")  


def main():

    args = parser.parse_args()

    output_path = unique_output_path(
        check_output_file_path_validity(args.output_path)
    )
    
    if args.file is not None:
        gif = process_to_gif(args.file)

    elif args.link is not None:
        gif = download_media_and_process(args.link)

    else:
        parser.print_help()

    write_gif_to_disk(gif, output_path)

    return 0

if __name__ == "__main__":
    main()
