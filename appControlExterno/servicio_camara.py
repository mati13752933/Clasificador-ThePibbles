import threading
import time
import cv2
from queue import Queue
import pyautogui
from .funciones_camara import detectar_gesto
from .estado_control import estado_archivo


class ServicioCamara:
    def __init__(self):
        self.camara_activa = False
        self.hilo = None
        self.cola = Queue()
        self._ultimo_gesto = None
        self._tiempo_ultimo = 0

    def iniciar(self):
        if not self.camara_activa:
            self.camara_activa = True
            self.cola = Queue()
            self._ultimo_gesto = None
            self._tiempo_ultimo = 0
            self.hilo = threading.Thread(target=self._loop_camara, daemon=True)
            self.hilo.start()

    def detener(self):
        self.camara_activa = False
        self._ultimo_gesto = None
        self._tiempo_ultimo = 0
        while not self.cola.empty():
            self.cola.get()

    def obtener_siguiente_gesto(self):
        if self.cola.empty():
            return None
        resultado = self.cola.get()
        self._ultimo_gesto = None
        return resultado

    def _procesar_gesto_archivos(self, gesto):
        if gesto == "archivo_bajar":
            pyautogui.press("down")
            estado_archivo.archivo_actual += 1
            return {
                "ok": True,
                "accion": "mensaje",
                "mensaje": f"Posicionado en archivo {estado_archivo.archivo_actual}."
            }
        if gesto == "archivo_subir":
            pyautogui.press("up")
            if estado_archivo.archivo_actual > 1:
                estado_archivo.archivo_actual -= 1
            return {
                "ok": True,
                "accion": "mensaje",
                "mensaje": f"Posicionado en archivo {estado_archivo.archivo_actual}."
            }

        if gesto == "archivo_seleccionar":
            pyautogui.press("enter")
            estado_archivo.desactivar()
            return {
                "ok": True,
                "accion": "mensaje",
                "mensaje": "Archivo seleccionado, clasificando."
            }

        if gesto == "archivo_cerrar":
            pyautogui.press("esc")
            estado_archivo.desactivar()
            return {
                "ok": True,
                "accion": "mensaje",
                "mensaje": "Selección de archivo cancelada."
            }

        return None

    def _procesar_gesto_navegacion(self, gesto):
        if gesto == "detener":
            return {
                "ok": True,
                "accion": "detener_camara",
                "mensaje": "Cámara detenida."
            }

        if gesto == "inicio":
            return {
                "ok": True,
                "accion": "redirigir",
                "ruta": "/",
                "mensaje": "Volviendo al inicio."
            }

        if gesto == "clasificacion":
            return {
                "ok": True,
                "accion": "redirigir",
                "ruta": "/clasificacion/",
                "mensaje": "Abriendo clasificación."
            }

        if gesto == "reportes":
            return {
                "ok": True,
                "accion": "redirigir",
                "ruta": "/reportes/",
                "mensaje": "Abriendo reportes."
            }

        if gesto == "perfil":
            return {
                "ok": True,
                "accion": "redirigir",
                "ruta": "/perfil/",
                "mensaje": "Abriendo perfil."
            }

        if gesto == "capturar_clasificacion":
            return {
                "ok": True,
                "accion": "capturar_clasificacion",
                "mensaje": "Listo para capturar y clasificar."
            }

        if gesto == "subir_imagen":
            return {
                "ok": True,
                "accion": "abrir_selector_imagen",
                "ruta": "/clasificacion/?accion=subir_imagen",
                "mensaje": "Abriendo selector de imagen."
            }

        return None

    def _loop_camara(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.camara_activa = False
            return

        COOLDOWN = 4.0 if estado_archivo.esta_activo() else 2.0
        TIEMPO_PARA_CONFIRMAR = 0.6

        gesto_estable = None
        tiempo_estable = None

        while cap.isOpened() and self.camara_activa:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            modo = estado_archivo.esta_activo()
            gesto, frame_anotado = detectar_gesto(frame, modo_archivos=modo)

            ahora = time.time()

            if gesto:
                if gesto != gesto_estable:
                    gesto_estable = gesto
                    tiempo_estable = ahora
                else:
                    tiempo_sostenido = ahora - tiempo_estable
                    tiempo_desde_ultimo = ahora - self._tiempo_ultimo

                    if tiempo_sostenido >= TIEMPO_PARA_CONFIRMAR and tiempo_desde_ultimo >= COOLDOWN:
                        self._ultimo_gesto = gesto
                        self._tiempo_ultimo = ahora
                        gesto_estable = None
                        tiempo_estable = None
                        print(f"[Cámara] modo_archivos={modo}, gesto={gesto}")
                        if modo and estado_archivo.esta_listo():
                            resultado = self._procesar_gesto_archivos(gesto)
                        elif modo:
                            resultado = None  
                        else:
                            resultado = self._procesar_gesto_navegacion(gesto)

                        if resultado:
                            if resultado.get("accion") == "detener_camara":
                                self.cola.put(resultado)
                                print(f"[Cámara] Gesto confirmado: {gesto} → deteniendo")
                                break

                            self.cola.put(resultado)
                            print(f"[Cámara] Gesto confirmado: {gesto} → {resultado['accion']}")
            else:
                gesto_estable = None
                tiempo_estable = None

            cv2.imshow("Control por cámara - The Pibbles", frame_anotado)

            if cv2.waitKey(1) & 0xFF == ord('s'):
                self.camara_activa = False
                break

        cap.release()
        cv2.destroyAllWindows()
        self.camara_activa = False