import pandas as pd
from pathlib import Path


class ConfigLoader:
    """
    Loads Configuration for Experiment:
    -----------------------------------
    config from a clean Excel file.
    One row = one configuration
    Blank cells = use default values.
    """

    def __init__(self, excel_path: str):
        """
        Loads Configuration for Experiment:
        ----------------------------------

        :param self: Object itself
        :param excel_path: Path for Config.xlsx
        :type excel_path: string
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.excel_path}")

    def load_configs(self, start_id: str, end_id: str):
        """
        Loads the Configuration in range start, end:
        -------------------------------------------

        :param start_id: Starting configuration
        :param end_id: Ending configuration
        """

        df = pd.read_excel(self.excel_path)

        if "config_id" not in df.columns:
            raise ValueError("Missing required column: config_id")

        df = df.set_index("config_id")

        if start_id not in df.index:
            raise ValueError(f"Start config not found: {start_id}")

        if end_id not in df.index:
            raise ValueError(f"End config not found: {end_id}")

        start_pos = df.index.get_loc(start_id)
        end_pos = df.index.get_loc(end_id)

        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos

        sliced = df.iloc[start_pos:end_pos + 1]

        configs = []
        for cfg_id, row in sliced.iterrows():
            params = {
                k: v for k, v in row.items()
                if pd.notna(v)
            }

            configs.append({
                "config_id": cfg_id,
                "params": params
            })

        return configs

    
# if __name__ == "__main__":
#     a = ConfigLoader(r"S:\Sambhav's Project\Config.xlsx")
#     r = a.load_configs("Config_A_01","Config_A_17")
#     print(r)
