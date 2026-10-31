import json

class ManejadorJSON:
    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo
        self.datos = []

    def importar(self):
        with open(self.ruta_archivo, mode='r', encoding='utf-8') as f:
            self.datos = json.load(f)
        print(f"JSON importado correctamente: {len(self.datos)} objetos cargados.")

    def agregar_registro(self, nuevo_registro: dict):
        self.datos.append(nuevo_registro)
        print(f"Nuevo registro agregado al JSON: {nuevo_registro['producto'] if 'producto' in nuevo_registro else ''}")

    def guardar(self, nueva_ruta: str):
        with open(nueva_ruta, mode='w', encoding='utf-8') as f:
            json.dump(self.datos, f, indent=2, ensure_ascii=False)
        print(f"Nuevo archivo JSON guardado exitosamente en: {nueva_ruta}")
