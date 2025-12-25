from pathlib import Path
import json


class RTTMGenerator:
    """
    Converts WhisperX diarized JSON → RTTM format
    """

    def json_to_rttm(self, audio_id: str, json_path: Path) -> str:
        """
        Returns RTTM text string
        """

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        lines = []

        for seg in data.get("segments", []):

            start = float(seg["start"])
            end = float(seg["end"])
            dur = end - start
            spk = seg.get("speaker", "UNK")

            # safety check
            if dur <= 0:
                continue

            line = (
                f"SPEAKER {audio_id} 1 "
                f"{start:.3f} {dur:.3f} "
                f"<NA> <NA> {spk} <NA>"
            )

            lines.append(line)

        return "\n".join(lines)
