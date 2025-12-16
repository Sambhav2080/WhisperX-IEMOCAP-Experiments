import json
from pathlib import Path
from analyser.base.file_manager import FileManager


class WERIO:
    """
    Loads reference TXT and hypothesis JSON.
    """

    def load_reference(self, txt_path: Path) -> str:
        FileManager.validate_file(txt_path)

        texts = []

        for line in txt_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue

            # 1️⃣ Try tab-separated (preferred)
            if "\t" in line:
                parts = line.split("\t")
                if len(parts) >= 4:
                    texts.append(parts[-1])
                    continue

            # 2️⃣ Fallback: split by spaces (last token(s) as text)
            parts = line.split()
            if len(parts) >= 4:
                # assume first 3 are: utt_id, start, end
                text = " ".join(parts[3:])
                texts.append(text)

        return " ".join(texts)


    def load_hypothesis_from_json(self, json_path: Path) -> str:
            """
            Load WhisperX JSON and extract hypothesis text.
            """
            FileManager.validate_file(json_path)

            data = json.loads(json_path.read_text(encoding="utf-8"))

            # WhisperX JSON structure:
            # data["segments"] -> list of segments
            # each segment has "text"
            texts = []

            for segment in data.get("segments", []):
                text = segment.get("text", "").strip()
                if text:
                    texts.append(text)

            # concatenate all segments into one string
            return " ".join(texts)

