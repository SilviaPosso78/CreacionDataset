import pandas as pd
import io

class DatasetSummarizer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def generate_summary(self, output_filename: str = "resumen_dataset.txt"):
        """Genera un archivo .txt con la estructura, tipos de datos, nulos y estadísticas."""
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str = buffer.getvalue()

        summary_content = []
        summary_content.append("=" * 50)
        summary_content.append("RESUMEN DEL DATAFRAME TRANSFORMADO")
        summary_content.append("=" * 50)
        summary_content.append(f"\nDimensiones: {self.df.shape[0]} filas, {self.df.shape[1]} columnas\n")

        summary_content.append("--- INFORMACIÓN GENERAL Y TIPOS DE DATOS ---")
        summary_content.append(info_str)

        summary_content.append("\n--- VALORES NULOS POR COLUMNA ---")
        summary_content.append(str(self.df.isnull().sum()))

        summary_content.append("\n--- ESTADÍSTICAS DESCRIPTIVAS ---")
        summary_content.append(str(self.df.describe(include='all')))

        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_content))

        print(f"Resumen guardado exitosamente en '{output_filename}'")
