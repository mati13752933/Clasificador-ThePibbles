import threading
import time
from queue import PriorityQueue
from Libreria.thepibbles.Audio.stt import Audio
from Libreria.thepibbles.Audio.tts import Voz
from .interprete import interpretar_comando
import pyautogui
from .estado_control import estado_archivo


class ServicioVoz:
    def __init__(self):
        self.audio = Audio()
        self.voz = Voz()
        self.cola = PriorityQueue()
        self.escuchando = False
        self.pausado = False
        self.hilo = None

    def iniciar(self):
        if not self.escuchando:
            self.escuchando = True
            self.pausado = False
            self.hilo = threading.Thread(target=self._escuchar_siempre, daemon=True)
            self.hilo.start()

    def detener(self):
        self.escuchando = False
        self.pausado = False
    
    def pausar(self):
        self.pausado = True
    
    def reanudar(self):
        if self.escuchando:
            self.pausado = False

   
    def procesar_comando_archivos(self, texto):
        if "bajar" in texto or "abajo" in texto or "siguiente" in texto:
            pyautogui.press("down")
            estado_archivo.archivo_actual += 1

            return {
                "ok": True,
                "accion": "mensaje",
                "mensaje": f"Posicionado en archivo {estado_archivo.archivo_actual}."
            }

        if "subir" in texto or "arriba" in texto or "anterior" in texto:
            pyautogui.press("up")

            if estado_archivo.archivo_actual > 1:
                estado_archivo.archivo_actual -= 1

            return {
                "ok": True,
                "accion": "mensaje",
                "mensaje": f"Posicionado en archivo {estado_archivo.archivo_actual}."
            }

        if "seleccionar" in texto or "elegir" in texto or "aceptar" in texto:
            pyautogui.press("enter")
            estado_archivo.desactivar()

            return {
                "ok": True,
                "mensaje": "Archivo seleccionado y clasificando."
            }

        if "cancelar" in texto or "salir" in texto or "cerrar" in texto:
            pyautogui.press("esc")
            estado_archivo.desactivar()

            return {
                "ok": True,
                "accion": "mensaje",
                "mensaje": "Selección de archivo cancelada."
            }

        return {
            "ok": False,
            "accion": "desconocido",
            "mensaje": "Comando de archivo no reconocido."
        }
    

    def _escuchar_siempre(self):
        while self.escuchando:
            if self.pausado:
                time.sleep(0.2)
                continue

            texto = self.audio.escuchar()
            if texto:
                texto_limpio = texto.lower().strip()

                if estado_archivo.esta_activo():
                    resultado = self.procesar_comando_archivos(texto_limpio)

                    if resultado:
                        prioridad = self.obtener_prioridad(resultado)
                        self.cola.put((prioridad, time.time(), texto, resultado))
                        continue


                resultado = interpretar_comando(texto)
                print("Comando interpretado:", resultado)

                prioridad = self.obtener_prioridad(resultado)
                self.cola.put((prioridad, time.time(), texto, resultado))
            
            time.sleep(0.2)

    def obtener_prioridad(self, resultado):
        if not resultado.get("ok"):
            return 9

        intencion = resultado.get("accion")

        prioridades = {
            "abrir_selector_imagen": 3,
            "ir_clasificacion": 2,
            "ir_reportes": 2,
            "ir_perfil": 2,
            "ir_admin": 2,
            "ir_inicio": 2,
            "detener": 1,
            "mensaje": 1,
            "generar_reporte": 3,
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



       
