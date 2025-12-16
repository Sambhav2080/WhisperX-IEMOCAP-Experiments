from analyser.base.analyser_base import AnalyserBase


class DERCalculator(AnalyserBase):
    """
    Calculates Diarization Error Rate.
    """

    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.reference_rttm = None
        self.hypothesis_rttm = None
        self.der_value = None

    def load_inputs(self, reference_rttm, hypothesis_rttm):
        self.reference_rttm = reference_rttm
        self.hypothesis_rttm = hypothesis_rttm

    def preprocess(self):
        # filter untimed segments later
        pass

    def calculate(self):
        # pyannote DER later
        pass

    def save_result(self):
        result_path = self.output_dir / "der.txt"
        with open(result_path, "w") as f:
            f.write(f"DER: {self.der_value}\n")
