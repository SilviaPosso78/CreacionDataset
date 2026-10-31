import csv

class ManejadorCSV:
    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo
        self.datos = []
        self.encabezados = []

    def importar(self):
        with open(self.ruta_archivo, mode='r', encoding='utf-8') as f:
            lector = csv.reader(f)
            self.encabezados = next(lector)
            self.datos = list(lector)
        print(f"CSV importado correctamente: {len(self.datos)} registros cargados.")

    def modificar_registro(self, id_registro: str, columna: str, nuevo_valor: str):
        # Buscar el índice de la columna solicitada
        idx_col = self.encabezados.index(columna)
        modificado = False
        for fila in self.datos:
            if fila[0] == id_registro:  # El Id está en la primera columna
                fila[idx_col] = nuevo_valor
                modificado = True
                break
        if modificado:
            print(f"Registro ID {id_registro} modificado: {columna} -> {nuevo_valor}.")
        else:
            print(f"No se encontró el registro con ID {id_registro}.")

    def guardar(self, nueva_ruta: str):
        with open(nueva_ruta, mode='w', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerow(self.encabezados)
            escritor.writerows(self.datos)
        print(f"Nuevo archivo CSV guardado exitosamente en: {nueva_ruta}")
