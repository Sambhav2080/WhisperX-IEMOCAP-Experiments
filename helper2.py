# main2.py
"""
Processing script for Dataset folders created earlier.

Usage:
    python main2.py
It will ask for the Dataset root folder path (location1).
It will then iterate audio_id folders inside that dataset and:
  1) normalize transcript.txt -> transcript_norm.txt
  2) create/update speaker_map.json (maps Mxxx->"M", Fxxx->"F")
  3) generate <audio_id>.rttm (saved in same folder)
After processing the first folder it will ask for permission to continue processing remaining folders.
At the end it prints a combined table: normalized_lines | speaker_map_entries | rttm_entries
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# -------------------------
# Helper regexes & utils
# -------------------------
# Timestamp regex like [008.8900-010.5700] (floats)
TIMESTAMP_RE = re.compile(r'\[\s*(\d+\.\d+)\s*-\s*(\d+\.\d+)\s*\]')
# bracket token like [LAUGHTER] or [laughter] etc.
BRACKET_TOKEN_RE = re.compile(r'\[[^\]]+\]')
# Keep only a-z0-9 and spaces
NON_ALPHANUM_SPACE_RE = re.compile(r'[^a-z0-9\s]+')


class processing:
    def __init__(self, dataset_root: str):
        self.dataset_root = Path(dataset_root).expanduser().resolve()
        if not self.dataset_root.exists():
            raise FileNotFoundError(f"Dataset root not found: {self.dataset_root}")

        # Internal memory structures for validation
        # counts_normalized_lines[audio_id] = number of normalized utterance lines written
        self.counts_normalized_lines: Dict[str, int] = {}
        # counts_speaker_map[audio_id] = number of mapping entries stored
        self.counts_speaker_map: Dict[str, int] = {}
        # counts_rttm_entries[audio_id] = number of RTTM segments written
        self.counts_rttm_entries: Dict[str, int] = {}

    # -------------------------
    # FUNCTION 1: normalize_txt
    # Input: path to audio folder (Path)
    # Reads `transcript.txt` and writes `transcript_norm.txt`
    # Returns number of normalized lines written
    # also stores mapping of utterance_id -> (start, end, norm_text) in memory and returns it
    # -------------------------
    def normalize_txt(self, audio_folder: Path) -> Dict[str, Tuple[float, float, str]]:
        """
        Normalize the transcript in audio_folder/transcript.txt.
        - Remove bracket tokens like [LAUGHTER] (if left only, drop the line)
        - Remove timestamps if no dialog remains
        - Keep utterance-level mapping: utt_id -> (start, end, normalized_text)
        - Create transcript_norm.txt containing lines:
            <utt_id>\t<start>\t<end>\t<normalized_text>
        Returns dict of utterance -> (start, end, norm_text)
        """
        transcript_path = audio_folder / "transcript.txt"
        out_norm_path = audio_folder / "transcript_norm.txt"

        utt_map: Dict[str, Tuple[float, float, str]] = {}
        normalized_lines = []

        if not transcript_path.exists():
            # nothing to do
            self.counts_normalized_lines[audio_folder.name] = 0
            return utt_map

        with transcript_path.open("r", encoding="utf-8", errors="ignore") as fh:
            raw_lines = [ln.rstrip("\n") for ln in fh]

        for raw in raw_lines:
            line = raw.strip()
            if not line:
                continue

            # split the line at first space to get utt_id candidate
            parts = line.split(None, 1)
            if len(parts) == 0:
                continue
            utt_id_candidate = parts[0].strip()
            remainder = parts[1].strip() if len(parts) > 1 else ""

            # Basic sanity: utt_id should start with 'Ses' (common in IEMOCAP)
            if not utt_id_candidate.startswith("Ses"):
                # Sometimes transcripts may have different formatting; try another approach:
                # If line contains ":" (colon), try splitting at the last colon to get text part.
                if ":" in line:
                    # fallback parse
                    try:
                        utt_token, rest = line.split(":", 1)
                        utt_id_candidate = utt_token.strip().split()[0]
                        remainder = rest.strip()
                    except Exception:
                        continue
                else:
                    continue

            # If no colon and no remainder: likely just an id line -> skip
            if remainder == "" and ":" not in raw:
                # nothing to normalize (case like 'Ses01M_script03_2_M003')
                continue

            # Extract timestamp(s) from remainder using TIMESTAMP_RE
            ts_match = TIMESTAMP_RE.search(remainder)
            start = None
            end = None
            if ts_match:
                start = float(ts_match.group(1))
                end = float(ts_match.group(2))
                # remove this timestamp from remainder
                remainder = TIMESTAMP_RE.sub("", remainder).strip()

            # Remove other bracketed tokens like [LAUGHTER]
            # But preserve the rest of the sentence if there is other text
            # We will remove bracket chunks first
            # Count bracket tokens before removal
            bracket_tokens = BRACKET_TOKEN_RE.findall(remainder)
            remainder_no_brackets = BRACKET_TOKEN_RE.sub("", remainder).strip()

            # If after removing bracket tokens the remainder becomes empty,
            # and there was at least one bracket token -> then it's a "only bracket" utterance: drop it.
            if remainder_no_brackets == "":
                # If there was no timestamp too, skip entirely
                # If there was a timestamp and nothing else, drop line (user requested removal)
                continue

            # Now remainder_no_brackets contains text to be normalized
            norm = remainder_no_brackets.lower()
            # remove punctuation/special chars except spaces and alphanumeric
            norm = NON_ALPHANUM_SPACE_RE.sub(" ", norm)
            # collapse multiple spaces
            norm = re.sub(r"\s+", " ", norm).strip()

            if norm == "":
                # nothing to keep
                continue

            # If we have no timestamps from the original but there might be embedded timestamps earlier,
            # attempt to find any timestamp in the original raw using TIMESTAMP_RE (already done)
            # For safety, if start/end are None, set them to 0.0 and duration 0.0 in RTTM later.
            start_val = float(start) if start is not None else 0.0
            end_val = float(end) if end is not None else start_val

            # store mapping
            utt_map[utt_id_candidate] = (start_val, end_val, norm)
            normalized_lines.append((utt_id_candidate, start_val, end_val, norm))

        # Write normalized transcript file
        with out_norm_path.open("w", encoding="utf-8") as outfh:
            for utt_id, s, e, text in normalized_lines:
                outfh.write(f"{utt_id}\t{s:.4f}\t{e:.4f}\t{text}\n")

        # Save count
        self.counts_normalized_lines[audio_folder.name] = len(normalized_lines)
        return utt_map

    # -------------------------
    # FUNCTION 2: create_speaker_map
    # Reads transcript.txt (or normalized mapping) and creates speaker_map.json
    # speaker_map: maps speaker token like M000 -> "M", F001 -> "F"
    # Also returns number of mapping entries
    # -------------------------
    def create_speaker_map(self, audio_folder: Path, utt_map: Dict[str, Tuple[float, float, str]]) -> Dict[str, str]:
        """
        Build speaker_map.json inside each audio folder.
        The function inspects utterance IDs (like Ses01M_script03_2_M002) and extracts
        the trailing token (M002 / F001) then maps to "M" or "F".
        Returns the mapping dict and stores counts in memory.
        """
        # load existing speaker_map if present
        sp_map_path = audio_folder / "speaker_map.json"
        speaker_map: Dict[str, str] = {}

        if sp_map_path.exists():
            try:
                speaker_map = json.loads(sp_map_path.read_text(encoding="utf-8") or "{}")
            except Exception:
                speaker_map = {}

        # Build mapping from utt_map keys
        for utt_id in utt_map.keys():
            # utt_id usually ends with "_M000" or "_F001"
            parts = utt_id.split("_")
            if len(parts) == 0:
                continue
            last = parts[-1]
            # Some utt ids may not adhere exactly; check pattern
            if last.startswith("M") or last.startswith("F"):
                speaker_token = last  # e.g., M002
                speaker_label = "M" if last.startswith("M") else "F"
            else:
                # fallback: search for Mxxx or Fxxx inside utt_id
                m = re.search(r'([MF]\d{3,})', utt_id)
                if m:
                    speaker_token = m.group(1)
                    speaker_label = "M" if speaker_token.startswith("M") else "F"
                else:
                    # fallback to using first letter after 'Ses..' part
                    speaker_label = "M" if "M" in utt_id else ("F" if "F" in utt_id else "U")
                    speaker_token = last

            # store mapping if not already present
            if speaker_token not in speaker_map:
                speaker_map[speaker_token] = speaker_label

        # write back speaker_map.json
        try:
            sp_map_path.write_text(json.dumps(speaker_map, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[!] Error writing speaker_map.json for {audio_folder.name}: {e}")

        self.counts_speaker_map[audio_folder.name] = len(speaker_map)
        return speaker_map

    # -------------------------
    # FUNCTION 3: rttm_generator
    # Reads transcript_norm.txt (if present) or transcript.txt and creates <audio_id>.rttm
    # Use speaker_map to map speaker tokens (M000->M or F000->F) as RTTM speaker label
    # -------------------------
    def generate_rttm(self, audio_folder: Path, utt_map: Dict[str, Tuple[float, float, str]], speaker_map: Dict[str, str]) -> int:
        """
        Generate RTTM file from utt_map. Each RTTM segment line will be:
        SPEAKER <audio_id> 1 <start> <duration> <NA> <NA> <speaker_label> <NA> <NA>
        speaker_label is taken from speaker_map for the utterance's speaker token (Mxxx/Fxxx),
        or fallback to 'unknown'.
        Returns number of RTTM rows written.
        """
        audio_id = audio_folder.name
        rttm_path = audio_folder / f"{audio_id}.rttm"
        lines_written = 0
        rttm_lines = []

        # utt_map keys are utterance ids like Ses01M_script03_2_M002
        for utt_id, (start, end, text) in utt_map.items():
            duration = max(0.0, float(end) - float(start))
            # extract speaker token from utt_id
            parts = utt_id.split("_")
            if len(parts) > 0:
                last = parts[-1]
                if last in speaker_map:
                    sp_label = speaker_map[last]
                else:
                    # fallback: try pattern inside utt_id
                    m = re.search(r'([MF]\d{1,4})', utt_id)
                    if m:
                        tok = m.group(1)
                        sp_label = speaker_map.get(tok, ( "M" if tok.startswith("M") else ("F" if tok.startswith("F") else "unknown") ))
                    else:
                        sp_label = "unknown"
            else:
                sp_label = "unknown"

            # RTTM wants start and duration in seconds
            # If end==start (no timestamp), we write duration 0.0 (still a valid row)
            s = float(start)
            d = float(duration)
            # make a RTTM line
            # Format: SPEAKER <file-id> 1 <start> <duration> <NA> <NA> <speaker_label> <NA> <NA>
            rttm_line = f"SPEAKER {audio_id} 1 {s:.4f} {d:.4f} <NA> <NA> {sp_label} <NA> <NA>"
            rttm_lines.append(rttm_line)
            lines_written += 1

        # write rttm file
        try:
            with rttm_path.open("w", encoding="utf-8") as outf:
                for ln in rttm_lines:
                    outf.write(ln + "\n")
        except Exception as e:
            print(f"[!] Error writing RTTM for {audio_id}: {e}")
            lines_written = 0

        self.counts_rttm_entries[audio_folder.name] = lines_written
        return lines_written

    # -------------------------
    # RUN for one audio folder
    # -------------------------
    def process_one_folder(self, audio_folder: Path):
        print(f"\nProcessing folder: {audio_folder.name}")
        # 1) normalize transcript
        utt_map = self.normalize_txt(audio_folder)
        print(f"  Normalized utterances: {len(utt_map)}")

        # 2) create speaker_map.json using utt_map
        sp_map = self.create_speaker_map(audio_folder, utt_map)
        print(f"  Speaker map entries: {len(sp_map)}")

        # 3) generate rttm using utt_map + sp_map
        r_written = self.generate_rttm(audio_folder, utt_map, sp_map)
        print(f"  RTTM lines written: {r_written}")

    # -------------------------
    # RUN over dataset folders with permission after first processed
    # -------------------------
    def run_all(self):
        # list all audio_id folders in dataset_root (sorted)
        folders = sorted([p for p in self.dataset_root.iterdir() if p.is_dir()])
        if not folders:
            print("No audio folders found in dataset root.")
            return

        cont_after_first = False
        for i, folder in enumerate(folders):
            # Only process folders that have a transcript.txt (skip others)
            if not (folder / "transcript.txt").exists():
                print(f"Skipping {folder.name} (no transcript.txt found).")
                continue

            # process first folder always, then ask permission
            self.process_one_folder(folder)

            if i == 0:
                # ask permission to continue remaining
                ans = input("\nProcessed first folder. Continue processing remaining folders? (Y/N): ").strip().lower()
                if ans != "y":
                    print("Stopping as per user request after first folder.")
                    break
                else:
                    cont_after_first = True
                    continue

        # After finishing, print combined table with counts
        self.print_summary_table()

    # -------------------------
    # print combined table of counts
    # -------------------------
    def print_summary_table(self):
        # produce list of all unique audio ids encountered
        all_audio = sorted(set(
            list(self.counts_normalized_lines.keys()) +
            list(self.counts_speaker_map.keys()) +
            list(self.counts_rttm_entries.keys())
        ))

        # print header
        print("\n" + "=" * 72)
        print("SUMMARY: audio_id | normalized_lines | speaker_map_entries | rttm_entries")
        print("=" * 72)
        for aid in all_audio:
            nl = self.counts_normalized_lines.get(aid, 0)
            sm = self.counts_speaker_map.get(aid, 0)
            rt = self.counts_rttm_entries.get(aid, 0)
            print(f"{aid:35s}  {nl:6d}            {sm:6d}            {rt:6d}")
        print("=" * 72 + "\n")


# -------------------------
# MAIN
# -------------------------
def main():
    dataset = input("Enter Dataset root folder (location1) [e.g., S:\\Sambhav's Project\\Dataset]: ").strip()
    if not dataset:
        print("Dataset root required. Exiting.")
        return

    proc = processing(dataset)
    proc.run_all()


if __name__ == "__main__":
    main()
