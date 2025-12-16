from pathlib import Path


class FileManager:
    """
    Handles file discovery and validation.
    No calculation logic allowed here.
    """

    @staticmethod
    def validate_file(path: Path):
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    @staticmethod
    def create_if_missing(path: Path):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
