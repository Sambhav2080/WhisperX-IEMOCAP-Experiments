from pathlib import Path
from typing import List, Dict
from dataset.dataset_manager import DatasetManager
from results.excel_writer import ExcelWriter


class ExperimentManager:

    def __init__(self,
                dataset_dir: str,
                output_root: str,
                results_excel: str):

        self.dataset_dir = Path(dataset_dir)
        self.output_root = Path(output_root)
        self.results_excel = Path(results_excel)

        self._validate_paths()

    def _validate_paths(self):
        if not self.dataset_dir.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_dir}")

        self.output_root.mkdir(parents=True, exist_ok=True)
        self.results_excel.parent.mkdir(parents=True, exist_ok=True)


    def run_experiments(self,
                        configs: List[Dict],
                        audio_items: List[Dict]):
        """
        Main controller
        """

        print("\n===== Starting Experiment Pipeline =====\n")

        print(f"[INFO] Total audios found: {len(audio_items)}")
        print(f"[INFO] Total configs: {len(configs)}\n")

        for cfg in configs:

            cfg_id = cfg["config_id"]
            params = cfg["params"]

            if cfg_id.lower() == "config_default":
                print(f"[SKIP] Default config already evaluated.")
                continue

            print(f"\n=== Running Config: {cfg_id} ===")

            for item in audio_items:

                audio_id = item["audio_id"]
                audio_path = item["wav_path"]

                print(f"\n→ Processing Audio: {audio_id}")

                out_dir = self.output_root / "WhisperX_Output" / audio_id
                out_dir.mkdir(parents=True, exist_ok=True)

                self._run_whisperx(audio_path, out_dir, params)

                wer = self._compute_wer(audio_path, out_dir)
                der = self._compute_der(audio_path, out_dir)
                rtf = self._compute_rtf(audio_path, out_dir)

                ExcelWriter(self.results_excel).write_audio_result(
                    cfg_id, audio_id, wer, der, rtf
                )

            # OPTIONAL future hook:
            # ExcelWriter(self.results_excel).write_overall_result(cfg_id, avg_wer, avg_der, avg_rtf)

        print("\n===== All Experiments Completed =====\n")
    # ---------- Delegation Methods (only CALL others) ----------

    def _run_whisperx(self, audio_path, out_dir, params):
        """
        Delegates whisperx run
        """
        from whisperx_core.whisperX_runner import WhisperXRunner
        from whisperx_core.whisperx_configurator import WhisperXConfigurator

        model = WhisperXConfigurator().configure(params)
        runner = WhisperXRunner(model)
        runner.run(audio_path)
        runner.save(out_dir)


    def _compute_wer(self, audio_path, out_dir):
        from analyser.wer.wer_calculator import WERCalculator
        # call WER module
        # return value
        return 0.0


    def _compute_der(self, audio_path, out_dir):
        from analyser.der.der_calculator import DERCalculator
        # call DER module
        return 0.0


    def _compute_rtf(self, audio_path, out_dir):
        from orchestrator.rtf_calculator import RTFCalculator
        return 0.0


    def _save_results(self, cfg_id, audio_id, wer, der, rtf):
        ExcelWriter(self.results_excel).write_audio_result(
            cfg_id, audio_id, wer, der, rtf
        )


    def _compute_overall(self, cfg_id,wer,der,rtf):
        ExcelWriter(self.results_excel).write_overall_result(cfg_id,wer,der,rtf)
