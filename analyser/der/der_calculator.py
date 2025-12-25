from analyser.base.analyser_base import AnalyserBase
from pyannote.metrics.diarization import DiarizationErrorRate


class DERCalculator(AnalyserBase):

    def __init__(self, output_dir: str):
        super().__init__(output_dir)

        self.reference_ann = None
        self.hypothesis_ann = None
        self.der_value = None

    def load_inputs(self, reference_ann, hypothesis_ann):
        self.reference_ann = reference_ann
        self.hypothesis_ann = hypothesis_ann

    def preprocess(self):
        pass   # already cleaned earlier

    def calculate(self):

        metric = DiarizationErrorRate()

        self.der_value = metric(
            self.reference_ann,
            self.hypothesis_ann
        )

        return self.der_value

    def save_result(self):
        path = self.output_dir / "der.txt"
        with open(path, "w") as f:
            f.write(f"DER: {self.der_value:.4f}\n")


