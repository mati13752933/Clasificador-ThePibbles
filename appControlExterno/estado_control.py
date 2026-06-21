import time

class EstadoArchivo:
    def __init__(self):
        self.modo_archivos = False
        self.archivo_actual = 1
        self._activado_en = 0

    def activar(self):
        self.modo_archivos = True
        self.archivo_actual = 1
        self._activado_en = time.time()

    def desactivar(self):
        self.modo_archivos = False
        self.archivo_actual = 1
        self._activado_en = 0

    def esta_activo(self):
        return self.modo_archivos

    def esta_listo(self):
        return time.time() - self._activado_en > 3.0
estado_archivo = EstadoArchivo()