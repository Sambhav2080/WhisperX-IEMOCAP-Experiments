# orchestrator/pipeline_runner.py
from pathlib import Path
from config.config_loader import ConfigLoader
from dataset.dataset_manager import DatasetManager
from orchestrator.experiment_manager import ExperimentManager


class PipelineRunner:

    def __init__(self,
                 dataset_dir: str,
                 output_dir: str,
                 config_file: str,
                 results_excel: str):

        self.dataset_dir = dataset_dir
        self.output_dir = output_dir
        self.config_file = config_file
        self.results_excel = results_excel


    def run(self, start_config: str, end_config: str):

        print("\n===== INITIALIZING PIPELINE =====\n")

        # ---- Load Configs ----
        loader = ConfigLoader(self.config_file)
        configs = loader.load_configs(start_config, end_config)

        # ---- Dataset Manager ----
        dataset = DatasetManager(self.dataset_dir)
        audio_items = dataset.get_all_audio_files()

        # ---- Experiment Manager ----
        manager = ExperimentManager(
            dataset_dir=self.dataset_dir,
            output_root=self.output_dir,
            results_excel=self.results_excel
        )

        # ---- Run full pipeline ----
        manager.run_experiments(
            configs=configs,
            audio_items=audio_items
        )

        print("\n===== PIPELINE COMPLETE =====\n")
