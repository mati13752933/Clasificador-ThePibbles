
class EstadoArchivo:
    def __init__(self):
        self.modo_archivos = False
        self.archivo_actual = 1

    def activar(self):
        self.modo_archivos = True
        self.archivo_actual = 1

    def desactivar(self):
        self.modo_archivos = False
        self.archivo_actual = 1

    def esta_activo(self):
        return self.modo_archivos
   
estado_archivo = EstadoArchivo()



