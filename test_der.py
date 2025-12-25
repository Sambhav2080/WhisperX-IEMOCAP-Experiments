from pathlib import Path
from analyser.base.analyser_base import AnalyserBase
from analyser.der.der_io import DERIO
from analyser.der.der_preprocessor import DERPreprocessor
from analyser.utils.rttm_generator import RTTMGenerator
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
        pass

    def calculate(self):

        metric = DiarizationErrorRate(
            collar=0.25,
            skip_overlap=True
        )

        self.der_value = metric(self.reference_ann, self.hypothesis_ann)
        return self.der_value

    def save_result(self):
        path = self.output_dir / "der.txt"
        with open(path, "w") as f:
            f.write(f"DER: {self.der_value:.4f}\n")



# --------- TEST ---------

audio_id = "Ses01F_impro01"

ref_rttm = Path(r"S:\Sambhav's Project\Dataset") / audio_id / f"{audio_id}.rttm"
hyp_json = Path(r"S:\Sambhav's Project\Output\result.json")

io = DERIO()
prep = DERPreprocessor()
gen = RTTMGenerator()

# load & convert
ref_text = ref_rttm.read_text()
hyp_rttm = gen.json_to_rttm(audio_id, hyp_json)

# RTTM -> Annotation
ref_ann = io.rttm_to_annotation(ref_text)
hyp_ann = io.rttm_to_annotation(hyp_rttm)

# ---- CLEAN HERE ----
ref_ann = prep.clean(ref_ann)
hyp_ann = prep.clean(hyp_ann)

print("REF speakers:", ref_ann.labels())
print("HYP speakers:", hyp_ann.labels())

# calculate
calc = DERCalculator(output_dir=".")
calc.load_inputs(ref_ann, hyp_ann)
der = calc.calculate()
calc.save_result()

print("\n=======================")
print("FINAL DER =", der)
print("=======================\n")
