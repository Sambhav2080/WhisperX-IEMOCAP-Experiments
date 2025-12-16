from analyser.utils.text_normalizer import TextNormalizer

class WERPreprocessor:
    """
    Handles text normalization for WER.
    """

    def __init__(self):
        self.normalizer = TextNormalizer()

    def normalize_reference(self, text: str) -> str:
        """
        Normalize reference transcript.
        """
        return self.normalizer.normalize(text)


    def normalize_hypothesis(self, text: str) -> str:
        """
        Normalize hypothesis transcript.
        """
        return self.normalizer.normalize(text)
