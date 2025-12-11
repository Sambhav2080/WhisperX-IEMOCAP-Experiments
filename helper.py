"""
cleanup_generated_files.py

Usage (Windows):
python cleanup_generated_files.py --target_root "S:/Sambhav's Project/Dataset" --dry

Options:
--target_root : path to Dataset root containing audio folders
--dry         : if present, script will only list files that would be deleted (safe preview)
--backup      : by default script makes a zip backup; use --nobackup to skip backup (not recommended)

What it does:
- Scans each immediate subfolder of target_root (ignores dot folders)
- Collects generated files to remove:
    metadata.json, speaker_map.json, transcript_clean.txt,
    emotion_label.txt, tags.json, reference.rttm
  (adjust list inside FILES_TO_REMOVE if you want)
- Makes a zip backup with those files (under target_root/backups/)
- Deletes the files from disk (after backup)
- Prints summary
"""
import os, argparse, zipfile, datetime, shutil

FILES_TO_REMOVE = [
    "metadata.json",
    "speaker_map.json",
    "transcript_clean.txt",
    "emotion_label.txt",
    "tags.json",
    "reference.rttm"
]

def find_audio_folders(root):
    return sorted([os.path.join(root,d) for d in os.listdir(root)
                   if os.path.isdir(os.path.join(root,d)) and not d.startswith('.')])

def collect_files_to_delete(audio_folders):
    mapping = {}
    for f in audio_folders:
        files = []
        for name in FILES_TO_REMOVE:
            p = os.path.join(f, name)
            if os.path.exists(p):
                files.append(p)
        if files:
            mapping[f] = files
    return mapping

def make_backup(mapping, target_root):
    if not mapping:
        return None
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(target_root, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    zip_path = os.path.join(backup_dir, f"generated_files_backup_{now}.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for folder, files in mapping.items():
            for file in files:
                arcname = os.path.relpath(file, target_root)
                zf.write(file, arcname=arcname)
    return zip_path

def delete_files(mapping):
    deleted = []
    for folder, files in mapping.items():
        for f in files:
            try:
                os.remove(f)
                deleted.append(f)
            except Exception as e:
                print(f"[ERROR] Failed to delete {f}: {e}")
    return deleted

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target_root', required=True, help='Target dataset root (audio-wise folders present)')
    ap.add_argument('--dry', action='store_true', help='Dry run: list files only')
    ap.add_argument('--nobackup', action='store_true', help='Do not create zip backup (not recommended)')
    args = ap.parse_args()

    target_root = args.target_root
    if not os.path.isdir(target_root):
        print("[ERROR] target_root not found:", target_root)
        return

    audio_folders = find_audio_folders(target_root)
    mapping = collect_files_to_delete(audio_folders)

    if not mapping:
        print("[INFO] No generated files found to remove.")
        return

    total_files = sum(len(v) for v in mapping.values())
    print(f"[INFO] Found {total_files} files across {len(mapping)} folders to remove.")
    for folder, files in mapping.items():
        print(f"  {os.path.basename(folder)}: {len(files)} files")

    if args.dry:
        print("\n[DRY RUN] No files will be deleted. Re-run without --dry to perform deletion.")
        return

    # backup
    zip_path = None
    if not args.nobackup:
        print("[INFO] Creating backup zip...")
        zip_path = make_backup(mapping, target_root)
        if zip_path:
            print("[INFO] Backup created at:", zip_path)
        else:
            print("[WARN] Backup creation skipped/failed.")

    # delete
    confirm = input("Type YES to delete the listed files permanently: ").strip()
    if confirm != "YES":
        print("Aborting. No files deleted.")
        return

    deleted = delete_files(mapping)
    print(f"[DONE] Deleted {len(deleted)} files. See backup at {zip_path if zip_path else 'no backup'}")

if __name__ == "__main__":
    main()




'''
import argparse
from pathlib import Path
import sys

def valid_dir(path_str):
    p = Path(path_str).expanduser()
    if not p.exists() or not p.is_dir():
        raise argparse.ArgumentTypeError(f"Directory does not exist: {path_str}")
    return p

def parse_args():
    parser = argparse.ArgumentParser(description="Create empty folders for each audio ID.")
    parser.add_argument("--audio_dir", type=str, help="Path to audio directory")
    parser.add_argument("--dest", type=str, help="Destination root for creating ID folders")
    parser.add_argument("--ext_audio", type=str, default=".wav", help="Audio extension (default .wav)")
    return parser.parse_args()

def get_input_if_none(arg_value, prompt):
    if arg_value:
        return Path(arg_value).expanduser()
    return Path(input(prompt).strip()).expanduser()

def main():
    args = parse_args()

    audio_dir = get_input_if_none(args.audio_dir, "Enter path to audio directory: ")
    dest_root = get_input_if_none(args.dest, "Enter destination root folder: ")

    # Validations
    if not audio_dir.exists() or not audio_dir.is_dir():
        print(f"ERROR: audio_dir does not exist or is not a directory: {audio_dir}")
        sys.exit(1)

    if not dest_root.exists():
        try:
            dest_root.mkdir(parents=True, exist_ok=True)
            print(f"Created destination root: {dest_root}")
        except Exception as e:
            print(f"ERROR: Cannot create destination root {dest_root}: {e}")
            sys.exit(1)

    audio_ext = args.ext_audio if args.ext_audio.startswith('.') else '.' + args.ext_audio

    # Read audio files but ignore hidden files starting with "."
    audio_files = sorted([
        p for p in audio_dir.iterdir()
        if p.is_file()
        and not p.name.startswith('.')        # Ignore hidden files
        and p.suffix.lower() == audio_ext.lower()
    ])

    if not audio_files:
        print(f"No audio files with extension {audio_ext} found in {audio_dir}")
        sys.exit(0)

    total_created = 0

    for audio_path in audio_files:
        uid = audio_path.stem  # unique ID from audio filename

        target_folder = dest_root / uid
        target_folder.mkdir(parents=True, exist_ok=True)
        total_created += 1

        print(f"[OK] Created folder: {target_folder}")

    print("\nSummary:")
    print(f"Total audio files read: {len(audio_files)}")
    print(f"Total ID folders created: {total_created}")

if __name__ == "__main__":
    main()

'''



'''#!/usr/bin/env python3
"""
Copy audio files and their matching transcription files into per-ID folders.

Usage:
    python make_dataset.py --audio_dir "D:\...\wav" --txt_dir "D:\...\transcriptions" --dest "S:\Sambhav's Project\Dataset"

If you omit CLI args, the script will prompt you interactively.
"""

import argparse
from pathlib import Path
import shutil
import sys

def valid_dir(path_str):
    p = Path(path_str).expanduser()
    if not p.exists() or not p.is_dir():
        raise argparse.ArgumentTypeError(f"Directory does not exist: {path_str}")
    return p

def parse_args():
    parser = argparse.ArgumentParser(description="Organize audio + transcription into per-ID folders.")
    parser.add_argument("--audio_dir", type=str, help="Path to audio files directory (e.g. .../dialog/wav)")
    parser.add_argument("--txt_dir", type=str, help="Path to transcription files directory (e.g. .../dialog/transcriptions)")
    parser.add_argument("--dest", type=str, help="Destination root where per-ID folders will be created")
    parser.add_argument("--ext_audio", type=str, default=".wav", help="Audio extension to consider (default .wav)")
    parser.add_argument("--ext_text", type=str, default=".txt", help="Text extension to consider (default .txt)")
    return parser.parse_args()

def get_input_if_none(arg_value, prompt):
    if arg_value:
        return Path(arg_value).expanduser()
    p = Path(input(prompt).strip()).expanduser()
    return p

def main():
    args = parse_args()

    audio_dir = get_input_if_none(args.audio_dir, "Enter path to audio directory: ")
    txt_dir = get_input_if_none(args.txt_dir, "Enter path to transcription directory: ")
    dest_root = get_input_if_none(args.dest, "Enter destination root folder: ")

    # validations
    for p, name in [(audio_dir, "audio_dir"), (txt_dir, "txt_dir")]:
        if not p.exists() or not p.is_dir():
            print(f"ERROR: {name} does not exist or is not a directory: {p}")
            sys.exit(1)

    if not dest_root.exists():
        try:
            dest_root.mkdir(parents=True, exist_ok=True)
            print(f"Created destination root: {dest_root}")
        except Exception as e:
            print(f"ERROR: Cannot create destination root {dest_root}: {e}")
            sys.exit(1)

    audio_ext = args.ext_audio if args.ext_audio.startswith('.') else '.' + args.ext_audio
    text_ext = args.ext_text if args.ext_text.startswith('.') else '.' + args.ext_text

    audio_files = sorted([p for p in audio_dir.iterdir() if p.is_file() and not p.name.startswith('.') and p.suffix.lower() == audio_ext.lower()])
    if not audio_files:
        print(f"No audio files with extension {audio_ext} found in {audio_dir}")
        sys.exit(0)

    copied_count = 0
    missing_txt = []
    for audio_path in audio_files:
        # Unique id = filename without extension
        uid = audio_path.stem  # Ses01F_impro01 from Ses01F_impro01.wav

        target_folder = dest_root / uid
        target_folder.mkdir(parents=True, exist_ok=True)

        # Copy audio
        target_audio = target_folder / audio_path.name
        try:
            shutil.copy2(audio_path, target_audio)
        except Exception as e:
            print(f"[ERROR] Failed to copy audio {audio_path} -> {target_audio}: {e}")
            continue

        # Find matching txt in txt_dir (ignore files beginning with .)
        expected_txt_name = uid + text_ext
        txt_candidate = txt_dir / expected_txt_name

        # Also allow case-insensitive search if exact not found
        txt_found = None
        if txt_candidate.exists() and txt_candidate.is_file() and not txt_candidate.name.startswith('.'):
            txt_found = txt_candidate
        else:
            # scan for matching stem (ignore hidden files)
            for p in txt_dir.iterdir():
                if not p.is_file():
                    continue
                if p.name.startswith('.'):
                    continue
                if p.stem == uid and p.suffix.lower() == text_ext.lower():
                    txt_found = p
                    break

        if txt_found:
            target_txt = target_folder / txt_found.name
            try:
                shutil.copy2(txt_found, target_txt)
            except Exception as e:
                print(f"[ERROR] Failed to copy txt {txt_found} -> {target_txt}: {e}")
            else:
                copied_count += 1
                print(f"[OK] {uid}: copied audio and txt -> {target_folder}")
        else:
            missing_txt.append(uid)
            print(f"[WARN] {uid}: audio copied, but no matching txt found in {txt_dir} (expected {expected_txt_name})")

    print("\nSummary:")
    print(f"Total audio files processed : {len(audio_files)}")
    print(f"Total pairs copied           : {copied_count}")
    if missing_txt:
        print(f"Missing transcriptions for {len(missing_txt)} IDs. Example(s): {', '.join(missing_txt[:10])}")
        print("You can inspect their folders in the destination to see only the audio files.")

if __name__ == "__main__":
    main()'''
