from pathlib import Path
import json

class DERIO:

    @staticmethod
    def load_reference(txt_path: Path):
        """
        Loads reference diarization segments.
        Returns list of dicts:
        [
        {"speaker": "F", "start": 6.29, "end": 8.23},
        ...
        ]
        """
        ref_segments = []

        with open(txt_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 4:
                    continue

                start = float(parts[1])
                end = float(parts[2])

                # ignore 0 → 0 timestamps
                if start == 0 and end == 0:
                    continue

                spk_code = parts[0].split("_")[-1]   # F000 → F
                speaker = spk_code[0]                # take gender only

                ref_segments.append({
                    "speaker": speaker,
                    "start": start,
                    "end": end
                })

        return ref_segments


    @staticmethod
    def load_hypothesis(json_path: Path):
        """
        Loads whisperx json diarization segments.
        Assumes each segment has speaker + word timestamps.
        """
        hyp_segments = []

        with open(json_path, "r") as f:
            data = json.load(f)

        for seg in data["segments"]:
            speaker = seg.get("speaker", None)

            if not speaker:
                continue

            # use word-level timestamps if available
            if "words" in seg and seg["words"]:
                start = seg["words"][0]["start"]
                end = seg["words"][-1]["end"]
            else:
                start = seg["start"]
                end = seg["end"]

            if start ==0 and end == 0:
                continue

            hyp_segments.append({
                "speaker": speaker,
                "start": float(start),
                "end": float(end)
            })

        return hyp_segments
