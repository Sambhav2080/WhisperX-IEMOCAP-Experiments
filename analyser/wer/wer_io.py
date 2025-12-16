import json
from pathlib import Path
from analyser.base.file_manager import FileManager


class WERIO:
    """
    Loads reference TXT and hypothesis JSON.
    """

    def load_reference(self, txt_path: Path) -> str:
        FileManager.validate_file(txt_path)
        return txt_path.read_text(encoding="utf-8")

    def load_hypothesis_from_json(self, json_path: Path) -> str:
        FileManager.validate_file(json_path)
        data = json.loads(json_path.read_text(encoding="utf-8"))
        # extract text later
        return ""
