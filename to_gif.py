from yt_dlp import YoutubeDL
import ffmpeg

from tempfile import NamedTemporaryFile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from shutil import get_terminal_size
import logging


# Defaults
DEFAULT_FILE_NAME = "out.gif"
DEFAULT_LOG_PATH = Path(__file__).with_suffix(".log")
DEFAULT_GIF_RESOLUTION_PX = 480
DEFAULT_GIF_FPS = 15

PROGRAM_NAME = "to_gif.py"
PROGRAM_DESCRIPTION= "Use yt_dlp and ffmpeg to attempt to convert arbitrary media to .gif format."
FILE_INDEX_LIMIT = 1000 # used in unique_output_path

# Setup log file
LOGGER = logging.getLogger("Default")
LOGGER.setLevel(logging.INFO)

HANDLER = logging.FileHandler(DEFAULT_LOG_PATH, mode='w')
HANDLER.setFormatter(logging.Formatter("%(message)s"))

LOGGER.addHandler(HANDLER)


parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
    prog=PROGRAM_NAME,
    description=PROGRAM_DESCRIPTION,
)

parser.add_argument(
    '-o',
    "--output_path",
    type=Path,
    default=Path(".") / DEFAULT_FILE_NAME,
    help="Where to store the output gif.",
)

parser.add_argument(
    "--fps",
    type=int,
    default=DEFAULT_GIF_FPS,
    help="FPS of output gif."
)

parser.add_argument(
    '-res',
    "--resolution",
    type=int,
    default=DEFAULT_GIF_RESOLUTION_PX,
    help="resolution of output gif."
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
            "logger": LOGGER,
        }

    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])

    except:
        message = f"Error occurred during download. See logs at {DEFAULT_LOG_PATH.resolve()}. (Exit status 1)"

        print('\n', end='') 
        print_big_terminal_message(message, delim='!')
        LOGGER.error(message)

        exit(1)

    gif = process_to_gif(Path(f.name))

    return gif

    
def process_to_gif(path: Path, fps: int, resolution_pix: int) -> bytes:

    try:
        gif, _ = (
                ffmpeg.input(path).output(
                    "pipe:",
                    format="gif",
                    vf=f"fps={fps},scale={resolution_pix}:-1:flags=lanczos",
                ).run(capture_stdout=True, capture_stderr=True)
            )
    except ffmpeg.Error as e:

            # stdout logging
            message = f"{e.stderr.decode("utf-8", errors="replace")}"
            print_big_terminal_message(message, delim='!', close = False)
            LOGGER.error(message)

            message = f"Error in FFmpeg processing. See logs at {DEFAULT_LOG_PATH.resolve()}. (Exit status 1)"
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
    LOGGER.info(message)


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
        gif = process_to_gif(args.file, args.fps, args.resolution)

    elif args.link is not None:
        gif = download_media_and_process(args.link)

    else:
        parser.print_help()

    write_gif_to_disk(gif, output_path)

    return 0

if __name__ == "__main__":
    main()
