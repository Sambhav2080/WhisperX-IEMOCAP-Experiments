from pathlib import Path


class DatasetManager:
    """
    Single Responsibility:
    ----------------------
    Manage dataset structure and
    return audio file paths in a clean way.
    """

    def __init__(self, dataset_root: str):
        self.dataset_root = Path(dataset_root)
        

    def list_audio_ids(self):
        """
        Returns list of folder names = audio ids
        """
        return sorted(
            [folder.name for folder in self.dataset_root.iterdir() if folder.is_dir()]
        )

    def get_audio_info(self, audio_id: str):
        """
        Returns wav path for a given audio_id
        """
        folder = self.dataset_root / audio_id
        if not self.dataset_root.exists():
            raise FileNotFoundError(f"folder path not exist")


        wav_files = list(folder.glob("*.wav"))

        if not wav_files:
            raise FileNotFoundError(f"No wav found in {folder}")

        return {
            "audio_id": audio_id,
            "wav_path": wav_files[0]
        }

    def get_all_audio_files(self):
        """
        Returns list of dict for all audio ids
        """
        return [self.get_audio_info(aid) for aid in self.list_audio_ids()]


a = DatasetManager(r"S:\Sambhav's Project\Dataset_IEMOCAP")
print(a.get_all_audio_files())