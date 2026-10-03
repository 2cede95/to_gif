# **to_gif.py**

Uses [yt_dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/) python wrappers to attempt to convert some arbitrary video link/file into the .gif format. Output is saved to disk in the same directory as the script.

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

**For customization options see the help page `python to_gif.py --help` 

## Add to windows context menu (optional)
### Add the option in the context menu
1. Open regedit and navigate to 'HKEY_CLASSES_ROOT\*\shell'.
2. Create a key at the path 'HKEY_CLASSES_ROOT\*\shell\to_gif'.
3. Go into the key.
4. Double click on (Default).
5. Set the value to 'Convert to gif'

### Add the python script shell command
1. Create a new key under to_gif called "command" i.e. (HKEY_CLASSES_ROOT\*\shell\to_gif\command).
2. Double click on (Default).
3. Set the value to '"C:\Path\to\python.exe" "C:\Path\to\to_gif.py" --file "%1"'.

![Windows context menu item](./assets/regedit_example.gif)
