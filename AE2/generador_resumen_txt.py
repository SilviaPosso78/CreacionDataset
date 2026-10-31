class GeneradorResumenTXT:
    def __init__(self, url_csv: str, url_json: str,
                 archivo_csv_original: str, archivo_json_original: str,
                 registros_csv: int, registros_json: int,
                 cambios_csv: str, cambios_json: str,
                 ruta_salida_csv: str, ruta_salida_json: str,
                 clases_metodos: list):
        self.url_csv = url_csv
        self.url_json = url_json
        self.archivo_csv_original = archivo_csv_original
        self.archivo_json_original = archivo_json_original
        self.registros_csv = registros_csv
        self.registros_json = registros_json
        self.cambios_csv = cambios_csv
        self.cambios_json = cambios_json
        self.ruta_salida_csv = ruta_salida_csv
        self.ruta_salida_json = ruta_salida_json
        self.clases_metodos = clases_metodos

    def generar_reporte(self, ruta_resumen: str = "resumen.txt"):
        with open(ruta_resumen, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("        REPORTE DE PROCESAMIENTO AE2\n")
            f.write("=" * 50 + "\n\n")
            f.write("1. URL DE ORIGEN (Hugging Face):\n")
            f.write(f"   - CSV: {self.url_csv}\n")
            f.write(f"   - JSON: {self.url_json}\n\n")
            f.write("2. ARCHIVOS IMPORTADOS:\n")
            f.write(f"   - CSV: {self.archivo_csv_original}\n")
            f.write(f"   - JSON: {self.archivo_json_original}\n\n")
            f.write("3. REGISTROS PROCESADOS:\n")
            f.write(f"   - CSV: {self.registros_csv}\n")
            f.write(f"   - JSON: {self.registros_json}\n\n")
            f.write("4. MODIFICACIONES REALIZADAS:\n")
            f.write(f"   - CSV: {self.cambios_csv}\n")
            f.write(f"   - JSON: {self.cambios_json}\n\n")
            f.write("5. ARCHIVOS GUARDADOS:\n")
            f.write(f"   - CSV: {self.ruta_salida_csv}\n")
            f.write(f"   - JSON: {self.ruta_salida_json}\n\n")
            f.write("6. CLASES Y MÉTODOS UTILIZADOS:\n")
            for item in self.clases_metodos:
                f.write(f"   - {item}\n")
        print(f"Resumen generado correctamente en: '{ruta_resumen}'")
