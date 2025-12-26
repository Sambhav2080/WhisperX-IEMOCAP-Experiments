import json
from pathlib import Path


class DERPreprocessor:

    @staticmethod
    def load_reference(ref_path: Path):
        """
        Loads reference txt format:
        speaker   start   end   text
        """

        segments = []

        with open(ref_path) as f:
            for line in f:
                p = line.strip().split()

                spk = p[0]
                start = float(p[1])
                end = float(p[2])

                if start == 0 and end == 0:
                    continue

                segments.append({
                    "spk": spk[7],   # F/M
                    "start": start,
                    "end": end
                })

        return segments



    @staticmethod
    def load_hypothesis(json_path: Path):

        with open(json_path) as f:
            data = json.load(f)

        segments = []

        for seg in data["segments"]:

            if not seg["words"]:
                continue

            spk = seg.get("speaker", "UNK")

            word_start = seg["words"][0]["start"]
            word_end = seg["words"][-1]["end"]

            if word_start == 0 and word_end == 0:
                continue

            segments.append({
                "spk": spk,
                "start": word_start,
                "end": word_end
            })

        return segments
