*************************
YouTube Audio Extractor
*************************

A versatile command-line script for downloading audio from YouTube videos as MP3 files. It uses yt-dlp for downloading and ffmpeg for conversion, offering detailed progress, batch processing, and features to bypass throttling.

----------------
Features
----------------

- High-Quality Audio: Downloads the best available audio track by default.
- MP3 Conversion: Converts the downloaded audio to MP3 format.
  - -mp3fast: (Default) Fast conversion, prioritizing speed and quality.
  - -mp3128: Converts to a smaller 128kbps bitrate file.
- Detailed Progress: Separate, real-time progress bars for both downloading and FFmpeg conversion.
- Batch Processing: Download multiple URLs from a text file using the --list option.
- Overwrite Protection: Asks for confirmation before overwriting existing files, unless --overwrite is used.
- Anti-Throttling: Includes options to use browser cookies (--cookies) and limit download speed (-r, --limit-rate) to avoid connection errors from YouTube.
- Flexible Output: Specify a custom output filename (-o) or a destination directory (-dst).
- Intelligent Error Handling: Detects when you forget to quote a URL and provides a helpful warning.

----------------
Requirements
----------------

Before you begin, ensure you have the following installed and accessible in your system's PATH:

1. Python 3: The script is written for Python 3.
   - (https://www.python.org/downloads/)
2. yt-dlp: The core tool for interacting with YouTube.
   - (https://github.com/yt-dlp/yt-dlp#installation)
3. FFmpeg & FFprobe: Required for conversion, progress reporting, and metadata analysis. They are usually bundled together.
   - (https://ffmpeg.org/download.html)
4. colorama (Python library):
   pip install colorama

----------------
Installation
----------------

1. Make sure all the requirements listed above are installed.
2. Download the script `youtube_audio_extractor.py` to your computer.
3. (Optional on Linux/macOS) Make the script executable:
   chmod +x youtube_audio_extractor.py

----------------
Usage
----------------

Basic Command:
The script is run from your terminal. Always enclose the URL in double quotes ("") to prevent errors with special characters.

  python youtube_audio_extractor.py [OPTIONS] "YOUTUBE_URL"

Options:

  Option: -h, --short-help
  Description: Shows a brief help message.

  Option: --help
  Description: Shows a detailed help message with all options.

  Option: -o, --output FILENAME
  Description: Specifies a custom output filename. Only works for a single URL.

  Option: --list FILE
  Description: Provides a text file with a list of URLs to download (one per line).

  Option: -dst DIRECTORY
  Description: Specifies the destination directory for the output files.

  Option: --overwrite
  Description: Automatically overwrites existing files without asking for confirmation.

  Option: -mp3fast
  Description: (Default) Fast extraction to a high-quality MP3.

  Option: -mp3128
  Description: Converts the audio to a 128kbps MP3 for a smaller file size.

  Option: --cookies BROWSER
  Description: (Highly Recommended) Uses cookies from a browser (e.g., chrome, firefox). Helps avoid connection errors.

  Option: -r, --limit-rate RATE
  Description: Limits the download speed (e.g., 500K, 2M) to appear less like a bot.

  Option: --color
  Description: Enables colorful terminal output.

  Option: --pb
  Description: Shows a detailed progress bar for downloads.

  Option: --log [FILENAME]
  Description: Logs all operations to `yt-dlp.log` or a custom filename.

  Option: --debug
  Description: Shows all raw, verbose output from `yt-dlp` and `ffmpeg` for troubleshooting.

----------------
Examples
----------------

Example 1: Basic Download
This will download the audio from the URL and save it as `Video-Title.mp3` in the current directory.

  python youtube_audio_extractor.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

Example 2: Best Practice (Avoiding Blocks)
This is the recommended way to run the script to avoid connection timeouts. It uses your Chrome browser's cookies and limits the download speed to 2 MB/s.

  python youtube_audio_extractor.py --cookies chrome -r 2M "https://www.youtube.com/watch?v=..."

Example 3: Specific Quality and Output Name
Downloads the audio, converts it to 128kbps, and saves it as `my-song.mp3` in the `C:\Music` directory.

  python youtube_audio_extractor.py -mp3128 -dst "C:\Music" -o "my-song.mp3" "https://www.youtube.com/watch?v=..."

Example 4: Batch Download from a File
Reads all URLs from `links.txt` and downloads them into the `audio_files` sub-directory, automatically overwriting any duplicates.

  python youtube_audio_extractor.py --list links.txt --dst ./audio_files --overwrite

----------------
Important Note: Quoting URLs
----------------

Your command-line shell (especially on Windows) uses the ampersand (&) character for special commands. Many YouTube URLs contain this character. If you do not wrap the URL in double quotes (""), your shell will cut the URL short, leading to errors. The script has a built-in warning system for this, but the best practice is to always use quotes.

  - Correct: python script.py "https://youtube.com/watch?v=abc&list=123"
  - Incorrect: python script.py https://youtube.com/watch?v=abc&list=123

----------------
License
----------------

This project is licensed under the MIT License.
