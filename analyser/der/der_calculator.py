from itertools import permutations
from pathlib import Path
from analyser.der.der_io import DERIO


class DERCalculator:
    """
    Computes Diarization Error Rate (DER)
    using optimal speaker permutation mapping
    """

    def __init__(self):
        """
        ref_segments = list of dicts:
        [{"spk":"F", "start":6.29, "end":8.24}, ...]

        hyp_segments = list of dicts:
        [{"spk":"SPEAKER_00", "start":6.93, "end":7.29}, ...]
        """

        self.ref = None
        self.hyp = None

    def load_inputs(self,ref_path:str ,hyp_path: str):
        self.ref = DERIO.load_reference(ref_path)
        self.hyp= DERIO.load_hypothesis(hyp_path)


    # ---------- PUBLIC API ----------

    def calculate(self):

        speakers_ref = sorted(list({s["spk"] for s in self.ref}))
        speakers_hyp = sorted(list({s["spk"] for s in self.hyp}))

        # if hyp detects extra speakers, keep only first N
        speakers_hyp = speakers_hyp[:len(speakers_ref)]

        best_der = 999


        for perm in permutations(speakers_hyp):

            mapping = {hyp: ref for hyp, ref in zip(perm, speakers_ref)}

            mapped_hyp = [
                {
                    "spk": mapping[h["spk"]],
                    "start": h["start"],
                    "end": h["end"]
                }
                for h in self.hyp
                if h["spk"] in mapping
            ]

            der, breakdown = self._compute_der_score(self.ref, mapped_hyp)

            if der < best_der:
                best_der = der


        return round(best_der, 4),breakdown



    # ---------- CORE LOGIC ----------

    def _compute_der_score(self, ref, hyp):

        """
        DER = (Missed + FalseAlarm + Confusion) / TotalSpeech
        """

        total_speech = sum(s["end"] - s["start"] for s in ref)

        missed = 0
        false_alarm = 0
        confusion = 0

        for r in ref:
            overlap_same = 0
            overlap_other = 0

            for h in hyp:

                overlap = self._overlap(
                    r["start"], r["end"],
                    h["start"], h["end"]
                )

                if overlap <= 0:
                    continue

                if r["spk"] == h["spk"]:
                    overlap_same += overlap
                else:
                    overlap_other += overlap

            ref_duration = r["end"] - r["start"]

            missed += max(0, ref_duration - overlap_same - overlap_other)
            confusion += overlap_other

        # False alarm = hyp speech outside any ref speech
        for h in hyp:
            hyp_dur = h["end"] - h["start"]

            overlap_total = sum(
                max(0, self._overlap(
                    h["start"], h["end"],
                    r["start"], r["end"]
                ))
                for r in ref
            )

            false_alarm += max(0, hyp_dur - overlap_total)

        der = (missed + false_alarm + confusion) / total_speech

        breakdown = (missed,false_alarm,confusion,total_speech)

        return der, breakdown



    # ---------- HELPERS ----------

    def _overlap(self, s1, e1, s2, e2):
        return max(0.0, min(e1, e2) - max(s1, s2))
