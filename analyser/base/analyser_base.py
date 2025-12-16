from abc import ABC, abstractmethod
from pathlib import Path


class AnalyserBase(ABC):
    """
    Abstract base class for all analysers (WER / DER).
    Enforces a common structure.
    """

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def load_inputs(self, **kwargs):
        pass

    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def calculate(self):
        pass

    @abstractmethod
    def save_result(self):
        pass
