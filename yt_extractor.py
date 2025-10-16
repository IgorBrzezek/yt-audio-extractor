#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=========================
YouTube Audio Extractor
=========================

Info:
  Author: Igor Brzezek (igor.brzezek@gmail.com)
  GitHub: https://github.com/IgorBrzezek/yt-audio-download
  Version: 1.0
  Date: 15.10.2025
  
LICENSE:
  MIT License 

DESCRIPTION:
  This script allows users to extract audio tracks from YouTube videos and save them as MP3 files.
  It utilizes the powerful yt-dlp library for downloading and ffmpeg for audio conversion.
  The script is controlled via command-line options, allowing for batch processing,
  different audio quality settings, and customized output.

  BEST PRACTICE:
  Always enclose URLs in double quotes (" ") when running the script from the command line,
  especially if the URL contains special characters like '&'. This prevents the shell
  from misinterpreting the URL.
  Example: python yt_extractor.py "https://youtube.com/watch?v=...&list=..."

REQUIREMENTS:
  1. Python 3
  2. yt-dlp
  3. ffmpeg & ffprobe
  4. colorama (Python library): pip install colorama
  
LIST FILE:  
    Sample audio list exapmple for extraction (for example: list.txt)
    Any URL without quotation marks.

    URL1
    URL2
    URL3

SCRIPT OPTIONS:
  urls (positional):
    One or more YouTube video URLs. Enclose each URL in quotation marks.

  -h, --short-help:
    Shows a brief help message.

  --help:
    Shows a detailed help message.
    
  -o, --output FILENAME:
    Specifies a custom output filename (only for a single URL).

  --list FILE:
    Provides a text file with a list of URLs.

  -dst DIRECTORY:
    Specifies the destination directory.

  --overwrite:
    Automatically overwrite existing files without asking.

  -mp3fast (Default):
    Fastest extraction to a high-quality MP3.

  -mp3128:
    Converts audio to a 128kbps MP3 for smaller file size.

  --cookies BROWSER[:PROFILE]:
    The most effective method for avoiding connection errors and YouTube blocking.
    This makes the script "pretend" to be your logged-in browser by sending the
    same cookies. It helps bypass throttling, age restrictions, and allows
    downloading private or members-only videos if you have access on your account.

    HOW TO USE:
      Enter the name of your browser in lowercase. The script will automatically
      find the corresponding cookies file on your computer.

    EXAMPLES:
      --cookies chrome
      --cookies firefox
      --cookies edge
      --cookies brave

    PROFILE (for advanced users):
      If you use multiple profiles in your browser (e.g., personal and work),
      you can specify one by adding its name after a colon. You can find your
      profile name in your browser's settings.
      Firefox example: --cookies firefox:default-release
      Chrome example:  --cookies chrome:"Profile 1" (use quotes for names with spaces)
      In most cases, just the browser name is sufficient.

  -r, --limit-rate RATE:
    Limits the download speed (e.g., 500K, 2M) to appear less like a bot.

  --color, --pb, --log, --debug:
    Options for output styling, logging, and debugging.

EXAMPLES:
  # Recommended: Download using browser cookies to avoid errors
  python yt_extractor.py --cookies chrome "YOUTUBE_URL"

  # Download and automatically overwrite any existing file
  python yt_extractor.py --overwrite "YOUTUBE_URL"
"""


import argparse
import subprocess
import sys
import os
import logging
import re
import time
from pathlib import Path
from colorama import init

AUTHOR = 'Igor Brzezek'
AUTHOR_EMAIL = 'igor.brzezek@gmail.com'
VERSION = 1.0
DATE = '15.10.2025'

# --- ANSI Color Codes ---
class Colors:
    HEADER, OKBLUE, OKCYAN, OKGREEN, WARNING, FAIL, ENDC, BOLD, UNDERLINE = '', '', '', '', '', '', '', '', ''
    if sys.stdout.isatty():
        HEADER = '\033[95m'; OKBLUE = '\033[94m'; OKCYAN = '\033[96m'; OKGREEN = '\033[92m'
        WARNING = '\033[93m'; FAIL = '\033[91m'; ENDC = '\033[0m'; BOLD = '\033[1m'; UNDERLINE = '\033[4m'

def cprint(text, color="", use_color_flag=False, **kwargs):
    if use_color_flag:
        print(f"{color}{text}{Colors.ENDC}", **kwargs)
    else:
        print(text, **kwargs)

def create_arg_parser():
    parser = argparse.ArgumentParser(description="A Python script to extract audio from YouTube videos using yt-dlp and ffmpeg.", epilog="Example usage:\n  python yt_extractor.py --cookies chrome -r 2M \"<YOUTUBE_URL>\"", add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-h', '--short-help', action='store_true', help="Show a short help message and exit.")
    parser.add_argument('--help', action='store_true', help="Show this extensive help message and exit.")
    parser.add_argument('-o', '--output', type=str, metavar='FILENAME', help="Specify the output filename. Only works for a single URL.")
    parser.add_argument('--list', type=str, metavar='FILE', help="Path to a text file containing YouTube URLs (one per line).")
    parser.add_argument('-dst', type=str, metavar='DIRECTORY', help="Destination directory for the output MP3 files. Defaults to the current directory.")
    parser.add_argument('--overwrite', action='store_true', help="Automatically overwrite existing files without asking.")
    audio_group = parser.add_mutually_exclusive_group()
    audio_group.add_argument('-mp3fast', action='store_true', default=True, help="Extract audio to MP3 using a high-quality VBR. (This is the default option).")
    audio_group.add_argument('-mp3128', action='store_true', help="Convert audio to MP3 with a constant bitrate of 128kbps for a smaller file size.")
    parser.add_argument('--cookies', type=str, metavar='BROWSER', help="Use cookies from a browser (chrome, firefox, etc.) to bypass YouTube throttling.")
    parser.add_argument('-r', '--limit-rate', type=str, metavar='RATE', help="Limit download speed (e.g., 500K, 2M) to avoid being blocked.")
    parser.add_argument('--color', action='store_true', help="Display colorful status messages in the terminal.")
    parser.add_argument('--pb', action='store_true', help="Show a detailed progress bar during download, including size, speed, and ETA.")
    parser.add_argument('--log', nargs='?', const='yt-dlp.log', default=None, metavar='FILENAME', help="Enable logging to a file.")
    parser.add_argument('--debug', action='store_true', help="Show all raw output from yt-dlp and ffmpeg for debugging purposes.")
    parser.add_argument('urls', nargs='*', help="One or more YouTube video URLs. This is ignored if --list is used.")
    return parser

def print_help(parser, detailed=False):
    if not detailed:
        print(f"YouTube Audio Extractor v{VERSION} ({DATE})")
        print(f"Author: {AUTHOR} ({AUTHOR_EMAIL})\n")
        print("Usage: python yt_extractor.py [OPTIONS] [URLS...]\n")
        print("A tool to download YouTube audio.\n")
        print("Core Options:")
        print("  -o FILENAME           Specify custom output filename (for single URL).")
        print("  --list FILE           Provide a file with URLs to download.")
        print("  -mp3128               Convert to 128kbps MP3 (default is -mp3fast).")
        print("  -dst DIRECTORY        Set output directory.")
        print("  --overwrite           Automatically overwrite existing files.\n")
        print("Anti-Blocking Options (Recommended):")
        print("  --cookies BROWSER     Use cookies from a browser (e.g., chrome, firefox).")
        print("  -r, --limit-rate RATE Limit download speed (e.g., 500K, 2M).\n")
        print("Other Options:")
        print("  --color, --pb, --log, --debug, -h, --help")
    else:
        parser.print_help()
    sys.exit(0)

def run_command(command, args, custom_handler=None):
    if args.debug:
        cprint(f"Executing command: {' '.join(command)}", Colors.OKBLUE, args.color)
    if args.log:
        logging.info(f"Executing: {' '.join(command)}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='replace')
        if custom_handler:
            custom_handler(process, args)
        else:
            for line in iter(process.stdout.readline, ''):
                if args.debug: print(line, end='')
                if args.log: logging.info(line.strip())
        process.stdout.close()
        return process.wait() == 0
    except FileNotFoundError:
        cprint(f"Error: Command '{command[0]}' not found. Please ensure it is installed and in your system's PATH.", Colors.FAIL, args.color)
        if args.log: logging.critical(f"{command[0]} command not found.")
        sys.exit(1)
    except Exception as e:
        cprint(f"An unexpected error occurred: {e}", Colors.FAIL, args.color)
        if args.log: logging.critical(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    init()
    parser = create_arg_parser()
    args = parser.parse_args()

    if args.short_help: print_help(parser, detailed=False)
    if args.help: print_help(parser, detailed=True)

    if args.log:
        logging.basicConfig(filename=args.log, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        cprint(f"Logging enabled. Output will be saved to '{args.log}'", Colors.OKCYAN, args.color)
        logging.info("--- Script started ---")

    urls = []
    if args.list:
        try:
            with open(args.list, 'r') as f: urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            cprint(f"Error: The file '{args.list}' was not found.", Colors.FAIL, args.color)
            if args.log: logging.error(f"File not found: {args.list}")
            sys.exit(1)
    else:
        urls = args.urls
    
    youtube_params = ('list=', 'pp=', 't=', 'si=')
    for url_arg in urls:
        if any(url_arg.startswith(param) for param in youtube_params):
            cprint(f"BŁĄD: Wykryto argument, który wygląda jak część adresu URL ('{url_arg}').", Colors.FAIL, use_color_flag=True)
            cprint("Prawdopodobnie zapomniałeś umieścić cały link w cudzysłowie.", Colors.WARNING, use_color_flag=True)
            cprint("Przykład poprawnego użycia:", Colors.OKCYAN, use_color_flag=True)
            cprint('  python yt_extractor.py "https://www.youtube.com/watch?v=...&list=..."', use_color_flag=True)
            sys.exit(1)

    if not urls:
        cprint("Error: No URLs provided. Use arguments or --list option.", Colors.FAIL, args.color)
        if args.log: logging.error("No URLs provided.")
        sys.exit(1)
        
    if args.output and len(urls) > 1:
        cprint("Error: The -o/--output option can only be used when processing a single URL.", Colors.FAIL, args.color)
        if args.log: logging.error("Attempted to use -o/--output with multiple URLs.")
        sys.exit(1)

    destination_dir = Path(args.dst) if args.dst else Path.cwd()
    destination_dir.mkdir(parents=True, exist_ok=True)

    cprint(f"Found {len(urls)} file(s) to process.", Colors.HEADER, args.color)
    if args.log: logging.info(f"Starting processing of {len(urls)} URLs.")

    overall_start_time = time.monotonic()

    for i, url in enumerate(urls, 1):
        if len(urls) > 1:
            cprint(f"\n--- Processing file {i}/{len(urls)}: {url} ---", Colors.BOLD, args.color)
            if args.log: logging.info(f"--- Processing {i}/{len(urls)}: {url} ---")
        
        try:
            get_title_cmd = ['yt-dlp', '--encoding', 'utf-8', '--get-filename', '-o', '%(title)s', url]
            if args.cookies: get_title_cmd.extend(['--cookies-from-browser', args.cookies])
            video_title = subprocess.check_output(get_title_cmd, universal_newlines=True, encoding='utf-8').strip()
        except Exception as e:
            cprint(f"Could not get video metadata for URL {url}. Error: {e}", Colors.FAIL, args.color)
            continue

        output_filename = f"{video_title}.mp3"
        if args.output:
            output_filename = args.output if args.output.lower().endswith('.mp3') else f"{args.output}.mp3"
        
        final_filepath = destination_dir / output_filename

        if final_filepath.exists() and not args.overwrite:
            cprint(f"File '{final_filepath.name}' already exists.", Colors.WARNING, use_color_flag=args.color)
            choice = input("Overwrite? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                cprint("Skipping file.", Colors.OKCYAN, use_color_flag=args.color)
                if args.log: logging.info(f"Skipped file (already exists): {final_filepath}")
                continue
        
        # --- MIERZENIE CZASU START ---
        download_start_time = time.monotonic()
        
        temp_filename_template = f"temp_{os.getpid()}_{i}.%(ext)s"
        temp_filepath_template = destination_dir / temp_filename_template
        
        download_command = ['yt-dlp', '-f', 'bestaudio', '--no-mtime', '-o', str(temp_filepath_template)]
        if args.color: download_command.extend(['--color', 'always'])
        if args.pb: download_command.append('--progress')
        if args.debug: download_command.append('--verbose')
        if args.cookies: download_command.extend(['--cookies-from-browser', args.cookies])
        if args.limit_rate: download_command.extend(['--limit-rate', args.limit_rate])
        download_command.append(url)

        cprint("Step 1: Downloading audio track...", Colors.OKCYAN, args.color)
        
        temp_filepath = None
        try:
            get_filename_cmd = ['yt-dlp', '--encoding', 'utf-8', '--get-filename', '-f', 'bestaudio', '-o', str(temp_filepath_template), url]
            if args.cookies: get_filename_cmd.extend(['--cookies-from-browser', args.cookies])
            temp_filepath_str = subprocess.check_output(get_filename_cmd, universal_newlines=True, encoding='utf-8').strip()
            temp_filepath = Path(temp_filepath_str)
        except Exception as e:
            cprint(f"Could not determine temporary filename. Error: {e}", Colors.FAIL, args.color)
            continue
            
        download_success = run_command(download_command, args, download_progress_handler)
        download_duration = time.monotonic() - download_start_time
        
        if not download_success:
            cprint(f"Download failed for {url}.", Colors.FAIL, args.color)
            if temp_filepath and temp_filepath.exists(): os.remove(temp_filepath)
            continue

        try:
            cprint(f"\nStep 2: Converting to MP3 -> ({final_filepath.name})...", Colors.OKCYAN, args.color)
            
            conversion_start_time = time.monotonic()
            duration = get_duration(temp_filepath, args)
            
            convert_command = ['ffmpeg', '-i', str(temp_filepath), '-vn']
            if args.mp3128:
                convert_command.extend(['-b:a', '128k'])
            else: 
                convert_command.extend(['-q:a', '2'])
            convert_command.extend(['-progress', 'pipe:1', '-y', str(final_filepath)])

            conversion_success = run_command(convert_command, args, lambda p, a: conversion_progress_handler(p, a, duration))
            conversion_duration = time.monotonic() - conversion_start_time

            if conversion_success:
                cprint(f"\nSuccessfully created: {final_filepath}", Colors.OKGREEN, args.color)
                # --- WYŚWIETLANIE CZASÓW ---
                cprint(f"Download time:   {download_duration:.2f}s", Colors.OKGREEN, args.color)
                cprint(f"Conversion time: {conversion_duration:.2f}s", Colors.OKGREEN, args.color)
                cprint("--------------------", Colors.OKGREEN, args.color)
                cprint(f"Total time:      {(download_duration + conversion_duration):.2f}s", Colors.OKGREEN + Colors.BOLD, args.color)
            else:
                cprint(f"\nConversion failed for {temp_filepath}", Colors.FAIL, args.color)
        finally:
            if temp_filepath and temp_filepath.exists(): os.remove(temp_filepath)

    overall_duration = time.monotonic() - overall_start_time
    if len(urls) > 1:
        cprint(f"\nAll tasks completed. Total script time: {overall_duration:.2f}s", Colors.OKGREEN + Colors.BOLD, args.color)
    else:
        cprint("\nAll tasks completed.", Colors.OKGREEN + Colors.BOLD, args.color)

    if args.log: logging.info("--- Script finished ---")

def download_progress_handler(process, args):
    keywords_to_show = ('[youtube]', '[info]')
    was_last_line_progress = False
    for line in iter(process.stdout.readline, ''):
        stripped_line = line.strip()
        if not stripped_line: continue
        if args.log: logging.info(stripped_line)
        if args.debug:
            print(line, end='')
            continue
        
        is_progress_line = '[download]' in stripped_line and '%' in stripped_line
        is_essential_line = any(keyword in stripped_line for keyword in keywords_to_show)
        if is_progress_line:
            cprint(f"\r{stripped_line}  ", use_color_flag=args.color, end="")
            sys.stdout.flush()
            was_last_line_progress = True
        elif is_essential_line:
            if was_last_line_progress: print() 
            cprint(stripped_line, use_color_flag=args.color)
            sys.stdout.flush()
            was_last_line_progress = False

def get_duration(filepath, args):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(filepath)]
    try:
        duration_str = subprocess.check_output(command, universal_newlines=True)
        return float(duration_str)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        cprint(f"Could not get audio duration using ffprobe. Error: {e}", Colors.WARNING, use_color_flag=args.color)
        return 0

def conversion_progress_handler(process, args, total_duration):
    if total_duration == 0:
        cprint("Cannot show progress because audio duration is unknown.", use_color_flag=args.color)
        return
    for line in iter(process.stdout.readline, ''):
        if args.debug: print(line, end='')
        if args.log: logging.info(line.strip())
        if "out_time_us=" in line:
            us_str = re.search(r'out_time_us=(\d+)', line)
            if us_str:
                microseconds = int(us_str.group(1))
                percent = (microseconds / (total_duration * 1_000_000)) * 100 if total_duration > 0 else 100
                progress_text = f"\rConverting to mp3: {percent:.1f}%"
                cprint(progress_text, Colors.OKCYAN, use_color_flag=args.color, end="")
                sys.stdout.flush()

if __name__ == '__main__':
    main()