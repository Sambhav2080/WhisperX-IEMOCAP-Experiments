from pathlib import Path
from analyser.base.file_manager import FileManager
from pyannote.core import Annotation, Segment


class DERIO:
    """
    Handles RTTM loading and conversion
    """

    def load_rttm(self, rttm_path: Path):
        FileManager.validate_file(rttm_path)
        return rttm_path.read_text(encoding="utf-8")

    def rttm_to_annotation(self, rttm_text: str) -> Annotation:

        ann = Annotation()

        for line in rttm_text.splitlines():

            if not line.strip():
                continue

            parts = line.split()

            # RTTM expected:
            # SPEAKER <uri> 1 <start> <dur> <NA> <NA> <speaker> <NA>

            if len(parts) < 8:
                continue

            start = float(parts[3])
            dur = float(parts[4])
            end = start + dur
            speaker = parts[7]

            segment = Segment(start, end)

            ann[segment] = speaker

        return ann
