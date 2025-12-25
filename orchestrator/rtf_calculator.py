# orchestrator/rtf_calculator.py
import time
import wave
from pathlib import Path


class RTFCalculator:

    def measure(self, wav_path: Path, fn):

        start = time.time()
        fn()
        end = time.time()

        duration = self._get_duration(wav_path)

        return round((end - start) / duration, 4)


    def _get_duration(self, wav_path: Path):
        with wave.open(str(wav_path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
        return frames / float(rate)
