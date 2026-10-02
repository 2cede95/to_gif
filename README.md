# **to_gif.py**

Uses yt_dlp and ffmpeg python wrappers to attempt to convert some arbitrary media link/file into the .gif format. Output is saved to disk in the same directory as the script.

Install dependencies via:

```
pip install ffmpeg-python yt_dlp
```

A standalone ffmpeg installation is also required: see https://ffmpeg.org/ (ensure ffmpeg is in PATH)

## Usage
### Convert a Youtube video to a gif:
```
python to_gif.py --link "https://www.youtube.com/watch?v=[youtube video ID]"
```

### Convert an .mp4 file to a gif and name the output file:
```
python to_gif.py --file "path/to/video.mp4" -o example
```

**For cusomization options see the help page `python to_gif.py --help` 
