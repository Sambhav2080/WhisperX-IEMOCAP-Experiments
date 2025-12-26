# main_runner.py
from orchestrator.pipeline_runner import PipelineRunner


if __name__ == "__main__":

    dataset = r"S:\Sambhav's Project\Dataset_IEMOCAP"
    output  = r"S:\Sambhav's Project\Output"
    config  = r"S:\Sambhav's Project\Config.xlsx"
    results = r"S:\Sambhav's Project\results\result.xlsx"

    start = input().strip()
    end   = input().strip()

    PipelineRunner(
        dataset_dir=dataset,
        output_dir=output,
        config_file=config,
        results_excel=results
    ).run(start, end)
