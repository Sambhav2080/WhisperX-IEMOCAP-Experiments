# Helper.py
"""
Dataset preparation helper for IEMOCAP → single Dataset folder.

Behavior (this version):
- For each session (Session1..Session5) under IEMOCAP root:
    - copies .wav files to: DATASET_ROOT/<audio_id>/<audio_id>.wav
    - copies transcripts to: DATASET_ROOT/<audio_id>/transcript.txt
    - copies ALL categorical utterance files to: DATASET_ROOT/<audio_id>/emotions/<orig_filename>.txt
    - copies ALL attribute utterance files to: DATASET_ROOT/<audio_id>/attributes/<orig_filename>.txt
    - creates placeholder speaker_map.json and metadata.json if missing
    - writes a manifest.json summarizing files inside each audio folder
- Skips hidden files (starting with '.')
- Prints per-session summaries and per-audio manifest info
- Non-destructive: does not delete existing dataset content
"""

import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List

# ----------------------------
# GLOBAL VARIABLES (set by TakeInput)
# ----------------------------
DATASET_ROOT: Optional[Path] = None
IEMOCAP_ROOT: Optional[Path] = None

SESSIONS = ["Session1", "Session2", "Session3", "Session4", "Session5"]


class TakeInput:
    """
    Initialize global paths. Creates DATASET_ROOT if not exists.
    """

    def __init__(self, location1: str, location2: str):
        global DATASET_ROOT, IEMOCAP_ROOT
        DATASET_ROOT = Path(location1).expanduser().resolve()
        IEMOCAP_ROOT = Path(location2).expanduser().resolve()

        # Create dataset root dir if not exists
        DATASET_ROOT.mkdir(parents=True, exist_ok=True)

        print("\n[✔] INPUT PATHS INITIALIZED")
        print(f"   → Dataset Output (location1): {DATASET_ROOT}")
        print(f"   → IEMOCAP Root (location2):   {IEMOCAP_ROOT}\n")


class helper_class:
    """
    All processing functions live here.
    """

    @staticmethod
    def safe_copy(src: Path, dst: Path):
        """
        Copy file src -> dst. Ensure dst parent exists.
        """
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    @staticmethod
    def create_placeholders(target_folder: Path):
        """
        Create empty speaker_map.json and metadata.json if they don't exist.
        """
        speaker_map = target_folder / "speaker_map.json"
        metadata = target_folder / "metadata.json"

        if not speaker_map.exists():
            speaker_map.write_text(json.dumps({}, indent=2), encoding="utf-8")

        if not metadata.exists():
            metadata.write_text(json.dumps({}, indent=2), encoding="utf-8")

    @staticmethod
    def write_manifest(target_folder: Path):
        """
        Write manifest.json listing available files (wav, transcript, emotions, attributes)
        """
        manifest: Dict[str, List[str]] = {
            "wav": [],
            "transcript": [],
            "emotions": [],
            "attributes": []
        }

        # wav
        for f in target_folder.glob("*.wav"):
            manifest["wav"].append(f.name)

        # transcript
        t = target_folder / "transcript.txt"
        if t.exists():
            manifest["transcript"].append(t.name)

        # emotions
        emo_dir = target_folder / "emotions"
        if emo_dir.exists():
            for f in sorted(emo_dir.iterdir()):
                if f.is_file():
                    manifest["emotions"].append(f.name)

        # attributes
        atr_dir = target_folder / "attributes"
        if atr_dir.exists():
            for f in sorted(atr_dir.iterdir()):
                if f.is_file():
                    manifest["attributes"].append(f.name)

        (target_folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def process_all_sessions(self):
        """
        Iterate sessions and process each session's dialog folder.
        """
        global DATASET_ROOT, IEMOCAP_ROOT

        if DATASET_ROOT is None or IEMOCAP_ROOT is None:
            raise RuntimeError("DATASET_ROOT and IEMOCAP_ROOT must be initialized via TakeInput.")

        for session in SESSIONS:
            print("\n" + "=" * 72)
            print(f"PROCESSING {session}")
            print("=" * 72)

            dialog_path = IEMOCAP_ROOT / session / "dialog"

            wav_path = dialog_path / "wav"
            trans_path = dialog_path / "transcriptions"
            emo_root = dialog_path / "EmoEvaluation"
            cat_path = emo_root / "Categorical"
            atr_path = emo_root / "Attribute"

            # If dialog folder doesn't exist, skip session
            if not dialog_path.exists():
                print(f"[!] dialog folder not found: {dialog_path}. Skipping {session}.")
                continue

            # Do each step with existence checks
            wav_count = self.process_wav_files(wav_path) if wav_path.exists() else 0
            trans_count = self.process_transcriptions(trans_path) if trans_path.exists() else 0
            cat_count = self.process_categorical(cat_path) if cat_path.exists() else 0
            atr_count = self.process_attribute(atr_path) if atr_path.exists() else 0

            # After copying, create or update manifest for each audio folder related to this session
            session_index = SESSIONS.index(session) + 1
            session_prefix = f"Ses{session_index:02d}"
            session_folders = sorted([p for p in DATASET_ROOT.iterdir() if p.is_dir() and p.name.startswith(session_prefix)])

            # write manifest for each audio folder
            for folder in session_folders:
                self.create_placeholders(folder)
                self.write_manifest(folder)

            # Summaries
            print("\n[Summary for {}]".format(session))
            print(f"  WAV files copied (utterance-level):      {wav_count}")
            print(f"  Transcriptions copied (audio-level):    {trans_count}")
            print(f"  Categorical utterance files copied:     {cat_count}")
            print(f"  Attribute utterance files copied:       {atr_count}")
            print(f"  Unique audio folders (session prefix):  {len(session_folders)}")
            print(f"  Session prefix used:                    {session_prefix}")

            # Ask user to continue
            while True:
                ch = input("\nContinue to next session? (Y/N): ").strip().lower()
                if ch in ("y", "n"):
                    break
                print("Please answer Y or N.")
            if ch == "n":
                print("Stopping as per user request.")
                break

    def process_wav_files(self, wav_path: Path) -> int:
        """
        Copy .wav files: <wav_path>/*.wav -> DATASET_ROOT/<audio_id>/<audio_id>.wav
        """
        print("\n[🔊] Copying WAV files...")
        count = 0
        for file in sorted(wav_path.iterdir()):
            if not file.is_file():
                continue
            if file.name.startswith("."):
                continue
            if file.suffix.lower() != ".wav":
                continue

            audio_id = file.stem  # e.g., Ses01F_impro01 or Ses01F_script01_1
            target_folder = DATASET_ROOT / audio_id
            target_folder.mkdir(parents=True, exist_ok=True)

            dst = target_folder / f"{audio_id}.wav"
            try:
                self.safe_copy(file, dst)
            except Exception as e:
                print(f"  [!] Error copying {file} -> {dst}: {e}")
                continue

            # create placeholders if missing
            self.create_placeholders(target_folder)
            count += 1

        print(f"[✔] WAV copied: {count} files")
        return count

    def process_transcriptions(self, trans_path: Path) -> int:
        """
        Copy transcription .txt files: <trans_path>/*.txt -> DATASET_ROOT/<audio_id>/transcript.txt
        Filename expected: <audio_id>.txt
        """
        print("\n[📄] Copying Transcriptions...")
        count = 0
        for file in sorted(trans_path.iterdir()):
            if not file.is_file():
                continue
            if file.name.startswith("."):
                continue
            if file.suffix.lower() != ".txt":
                continue

            audio_id = file.stem
            target_folder = DATASET_ROOT / audio_id
            target_folder.mkdir(parents=True, exist_ok=True)

            dst = target_folder / "transcript.txt"
            try:
                self.safe_copy(file, dst)
            except Exception as e:
                print(f"  [!] Error copying transcription {file} -> {dst}: {e}")
                continue

            self.create_placeholders(target_folder)
            count += 1

        print(f"[✔] Transcriptions copied: {count} files")
        return count

    def process_categorical(self, cat_path: Path) -> int:
        """
        Copy ALL categorical utterance files into each audio folder's 'emotions' subfolder.
        Filenames example:
            Ses01F_impro02_e1_cat.txt
            Ses01F_script01_1_e2_cat.txt

        We determine audio_id by splitting on '_e' (everything before '_e' is audio_id).
        """
        print("\n[🎭] Copying Categorical Emotion Files (all utterances)...")
        count = 0
        if not cat_path.exists():
            print("  [!] Categorical folder does not exist.")
            return 0

        # iterate through all files and copy each to corresponding audio folder/emotions/
        for file in sorted(cat_path.iterdir()):
            if not file.is_file():
                continue
            if file.name.startswith("."):
                continue
            if file.suffix.lower() != ".txt":
                continue

            stem = file.stem
            # robust extraction: split on '_e' which precedes the emotion index (e.g., _e1_)
            if "_e" in stem:
                audio_id = stem.split("_e", 1)[0]
            else:
                parts = stem.split("_")
                if len(parts) >= 3 and parts[0].startswith("Ses"):
                    audio_id = "_".join(parts[:3])
                else:
                    audio_id = parts[0]

            target_folder = DATASET_ROOT / audio_id
            emo_dir = target_folder / "emotions"
            emo_dir.mkdir(parents=True, exist_ok=True)

            dst = emo_dir / f"{file.name}"
            try:
                self.safe_copy(file, dst)
            except Exception as e:
                print(f"  [!] Error copying categorical {file} -> {dst}: {e}")
                continue

            # ensure placeholders + manifest will be created later
            self.create_placeholders(target_folder)
            count += 1

        print(f"[✔] Categorical utterance files copied: {count} files")
        return count

    def process_attribute(self, atr_path: Path) -> int:
        """
        Copy ALL attribute utterance files into each audio folder's 'attributes' subfolder.
        Filenames example:
            Ses01F_impro02_e1_atr.txt
            Ses01F_script01_1_e3_atr.txt
        """
        print("\n[🧠] Copying Attribute Emotion Files (all utterances)...")
        count = 0
        if not atr_path.exists():
            print("  [!] Attribute folder does not exist.")
            return 0

        for file in sorted(atr_path.iterdir()):
            if not file.is_file():
                continue
            if file.name.startswith("."):
                continue
            if file.suffix.lower() != ".txt":
                continue

            stem = file.stem
            if "_e" in stem:
                audio_id = stem.split("_e", 1)[0]
            else:
                parts = stem.split("_")
                if len(parts) >= 3 and parts[0].startswith("Ses"):
                    audio_id = "_".join(parts[:3])
                else:
                    audio_id = parts[0]

            target_folder = DATASET_ROOT / audio_id
            atr_dir = target_folder / "attributes"
            atr_dir.mkdir(parents=True, exist_ok=True)

            dst = atr_dir / f"{file.name}"
            try:
                self.safe_copy(file, dst)
            except Exception as e:
                print(f"  [!] Error copying attribute {file} -> {dst}: {e}")
                continue

            self.create_placeholders(target_folder)
            count += 1

        print(f"[✔] Attribute utterance files copied: {count} files")
        return count


# -------------------------
# MAIN
# -------------------------
def main():
    print("\n========== DATASET PREPARATION TOOL (KEEP ALL UTTERANCE EMOTIONS) ==========\n")
    location1 = input("Enter Dataset Output Folder (location1) [e.g., S:\\Sambhav's Project\\Dataset]: ").strip()
    location2 = input("Enter IEMOCAP Dataset Folder (location2) [e.g., S:\\IEMOCAP_full_release]: ").strip()

    if not location1 or not location2:
        print("Both locations are required. Exiting.")
        return

    # Initialize global paths
    TakeInput(location1, location2)

    # Run processing
    helper = helper_class()
    helper.process_all_sessions()

    print("\n[✔] DATASET PROCESSING COMPLETED SUCCESSFULLY\n")


if __name__ == "__main__":
    main()
