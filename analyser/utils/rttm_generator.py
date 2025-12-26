import json
from pathlib import Path


class JSONtoRTTMConverter:

    def convert(self, json_path: Path, rttm_path: Path):
        """
        Convert WhisperX diarization JSON → RTTM
        """

        data = json.loads(json_path.read_text(encoding="utf-8"))

        with rttm_path.open("w", encoding="utf-8") as f:
            for seg in data["segments"]:

                if "speaker" not in seg:
                    # fallback if diarization disabled
                    speaker = "SPEAKER_00"
                else:
                    speaker = seg["speaker"]

                start = float(seg["start"])
                dur = float(seg["end"]) - float(seg["start"])

                line = (
                    f"SPEAKER file1 1 {start:.3f} {dur:.3f} "
                    f"<NA> <NA> {speaker} <NA> <NA>\n"
                )
                f.write(line)
