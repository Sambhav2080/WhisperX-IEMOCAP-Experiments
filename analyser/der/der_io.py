from pathlib import Path
from analyser.base.file_manager import FileManager


class DERIO:
    """
    Loads RTTM files.
    """

    def load_rttm(self, rttm_path: Path):
        FileManager.validate_file(rttm_path)
        return rttm_path.read_text(encoding="utf-8")
