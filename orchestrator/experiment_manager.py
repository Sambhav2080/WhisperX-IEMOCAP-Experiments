from pathlib import Path
from typing import List, Dict
from dataset.dataset_manager import DatasetManager
from results.excel_writer import ExcelWriter


class ExperimentManager:
    """
    Docstring for ExperimentManager
    -------------------------------
    """

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

            # remove this to run default config
            if cfg_id.lower() == "config_default":
                print(f"[SKIP] Default config already evaluated.")
                continue

            print(f"\n=== Running Config: {cfg_id} ===")

            Total_processing_Time = 0
            Total_audio_Time = 0

            reference_text = ""
            hypothesis_text = ""

            Total_reference_time = 0
            Total_miss = 0
            Total_False_alarm = 0
            Total_confusion = 0

            for item in audio_items:

                audio_id = item["audio_id"]
                audio_path = item["wav_path"]

                print(f"\n→ Processing Audio: {audio_id}")

                out_dir = self.output_root / "WhisperX_Output" / audio_id
                out_dir.mkdir(parents=True, exist_ok=True)

                processing_time = self._run_whisperx(audio_path, out_dir, params,audio_id)
                Total_processing_Time+=round(processing_time,4)

                res_wer = self._compute_wer(audio_id, out_dir)
                wer = res_wer[0]

                der,breakdown = self._compute_der(audio_id, out_dir)
                Total_miss += breakdown[0]
                Total_False_alarm +=breakdown[1]
                Total_confusion += breakdown[2]
                Total_reference_time += breakdown[3]

                res_time = self._compute_rtf(audio_path, processing_time)
                rtf = res_time[0]

                Total_audio_Time += res_time[1]
                reference_text += res_wer[1]
                hypothesis_text += res_wer[2]


                ExcelWriter(self.results_excel).write_audio_result(
                    cfg_id, audio_id, wer, der, rtf
                )

            #OVERALL RESULT CALCULATION:
            overall_result = self._compute_overall(
                cfg_id,
                reference_text,
                hypothesis_text,
                Total_processing_Time,
                Total_audio_Time,
                Total_miss,
                Total_False_alarm,
                Total_confusion,
                Total_reference_time
            )
            WER = overall_result[0]
            DER = overall_result[1]
            RTF = overall_result[2]
            ExcelWriter(self.results_excel).write_overall_result(cfg_id,WER,DER,RTF)
            

        print("\n===== All Experiments Completed =====\n")
    # ---------- Delegation Methods (only CALL others) ----------

    def _run_whisperx(self, audio_path, out_dir, params, audio_id):
        """
        Delegates whisperx run
        """
        from whisperx_core.whisperX_runner import WhisperXRunner
        from whisperx_core.whisperx_configurator import WhisperXConfigurator
        import time

        model = WhisperXConfigurator().configure(params)
        runner = WhisperXRunner(model)

        start = time.time()

        runner.run(audio_path)
        runner.save_result(out_dir,audio_id)

        end = time.time()

        return end-start

    def _compute_wer(self, audio_id, out_dir):
        """
        Deligate to compute wer
        """
        from analyser.wer.wer_calculator import WERCalculator
        from pathlib import Path

        ref_path = self.dataset_dir / audio_id /"transcript_norm.txt"   # reference
        hyp_path = out_dir / f"{audio_id}.json"        # whisper result

        calculator = WERCalculator(out_dir)
        calculator.load_inputs(ref_path,hyp_path)
        calculator.preprocess()
        wer = calculator.calculate()
        ref = calculator.get_ref_token()
        hyp = calculator.get_hyp_token()
        result = (round(wer,4),ref,hyp)

        return result


    def _compute_der(self, audio_id, out_dir):
        from analyser.der.der_calculator import DERCalculator
        # call DER module
        ref_path = self.dataset_dir / audio_id /"transcript_norm.txt"   # reference
        hyp_path = out_dir / f"{audio_id}.json"        # whisper result

        calculator = DERCalculator()
        calculator.load_inputs(ref_path,hyp_path)
        der,breakdown = calculator.calculate()

        return der,breakdown


    def _compute_rtf(self, audio_path,processing_time):
        from analyser.rtf.rtf_calculator import RTFCalculator
        calc = RTFCalculator()
        result = calc.calculate(audio_path,processing_time)
        return result


    def _save_results(self, cfg_id, audio_id, wer, der, rtf):
        ExcelWriter(self.results_excel).write_audio_result(
            cfg_id, audio_id, wer, der, rtf
        )

    def _compute_overall(self,cfg_id,ref,hyp,process_time,audio_time,miss,false_alarm,confusion,reference_time):
        from analyser.wer.wer_calculator import WERcalculator_overall

        calculate = WERcalculator_overall(ref,hyp)
        calculate.preprocess()
        WER = calculate.calculate()

        DER = round(((miss+false_alarm+confusion)/reference_time),4)

        RTF = round(process_time/audio_time,4)
        return [WER,DER,RTF]
    
        
