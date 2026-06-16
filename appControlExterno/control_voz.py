import threading
import time
from queue import PriorityQueue

from Libreria.thepibbles.Audio.stt import Audio
from Libreria.thepibbles.Audio.tts import Voz
from .interprete import interpretar_comando


class ServicioVoz:
    def __init__(self):
        self.audio = Audio()
        self.voz = Voz()
        self.cola = PriorityQueue()
        self.escuchando = False
        self.hilo = None

    def iniciar(self):
        if not self.escuchando:
            self.escuchando = True
            self.hilo = threading.Thread(target=self._escuchar_siempre, daemon=True)
            self.hilo.start()

    def detener(self):
        self.escuchando = False

    def _escuchar_siempre(self):
        while self.escuchando:
            texto = self.audio.escuchar()

            if texto:
                resultado = interpretar_comando(texto)
                print(f"Comando interpretado: {resultado}")
                prioridad = self.obtener_prioridad(resultado)

                self.cola.put((prioridad, time.time(), texto, resultado))

            time.sleep(0.2)

    def obtener_prioridad(self, resultado):
        if not resultado.get("ok"):
            return 9

        intencion = resultado.get("intencion")

        prioridades = {
            "abrir_selector_imagen": 2,
            "ir_clasificacion": 1,
            "ir_reportes": 1,
            "ir_perfil": 1,
            "ir_admin": 1,
            "ir_inicio": 1,
            "detener": 3
        }

        return prioridades.get(intencion, 8)

    def obtener_siguiente_comando(self):
        if self.cola.empty():
            return None

        prioridad, tiempo, texto, resultado = self.cola.get()

        return {
            "texto": texto,
            "resultado": resultado
        }


