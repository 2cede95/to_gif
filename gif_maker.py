from yt_dlp import YoutubeDL, utils
import ffmpeg

from tempfile import NamedTemporaryFile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from shutil import get_terminal_size
from sys import exit

parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
    prog="to_gif.py",
    description="Use yt_dlp and ffmpeg to attempt to convert arbitrary media to .gif format.",
)

parser.add_argument(
    '-o',
    "--output_path",
    type=Path,
    default=Path(".") / "out.gif",
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
                    vf="fps=15,scale=720:-1:flags=lanczos",
                ).run(capture_stdout=True, capture_stderr=True)
            )
    except ffmpeg.Error as e:

            message = f"{e.stderr.decode("utf-8", errors="replace")}"
            print_big_terminal_message(message, delim='!', close = False)

            message = f"Error in FFmpeg processing. See above logs for details. (Exit status 1)"
            print_big_terminal_message(message, delim='!', open = False)

            exit()

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

def main():

    args = parser.parse_args()
    
    if args.file is not None:
        gif = process_to_gif(args.file)
    elif args.link is not None:
        gif = download_media_and_process(args.link)
    else:
        parser.print_help()

    write_gif_to_disk(gif, args.output_path)

    return 0

if __name__ == "__main__":
    main()




