import pandas as pd
from datasets import load_dataset

class HFDatasetLoader:
    def __init__(self, dataset_name: str, split: str = "train"):
        self.dataset_name = dataset_name
        self.split = split

    def load_to_dataframe(self) -> pd.DataFrame:
        """Carga el dataset desde Hugging Face y lo convierte en DataFrame de pandas."""
        dataset = load_dataset(self.dataset_name, split=self.split)
        return dataset.to_pandas()
