from analyser.base.analyser_base import AnalyserBase


class WERCalculator(AnalyserBase):
    """
    Calculates Word Error Rate.
    """

    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.reference_text = None
        self.hypothesis_text = None
        self.wer_value = None

    def load_inputs(self, reference_text: str, hypothesis_text: str):
        self.reference_text = reference_text
        self.hypothesis_text = hypothesis_text

    def preprocess(self):
        # will call text normalizer later
        pass

    def calculate(self):
        # actual WER logic later
        pass

    def save_result(self):
        result_path = self.output_dir / "wer.txt"
        with open(result_path, "w") as f:
            f.write(f"WER: {self.wer_value}\n")
