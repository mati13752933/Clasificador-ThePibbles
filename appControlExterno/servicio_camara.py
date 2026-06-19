import threading
import time
import cv2
from queue import Queue
from .funciones_camara import detectar_gesto


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
        # Vacía la cola
        while not self.cola.empty():
            self.cola.get()

    def obtener_siguiente_gesto(self):
        if self.cola.empty():
            return None
        gesto = self.cola.get()
        # Resetea para permitir el mismo gesto en la próxima página
        self._ultimo_gesto = None
        return gesto

    def _loop_camara(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.camara_activa = False
            return

        COOLDOWN = 2.0  # segundos entre gestos
        gesto_estable = None
        tiempo_estable = None
        TIEMPO_PARA_CONFIRMAR = 0.6  # el gesto debe mantenerse 0.6s para confirmarse

        while cap.isOpened() and self.camara_activa:
            ret, frame = cap.read()

            if not ret:
                break

            frame = cv2.flip(frame, 1)
            gesto, frame_anotado = detectar_gesto(frame)
            ahora = time.time()

            if gesto:
                # Si es un gesto nuevo, empezamos a cronometrar
                if gesto != gesto_estable:
                    gesto_estable = gesto
                    tiempo_estable = ahora
                else:
                    # Si lleva suficiente tiempo estable, lo encolamos
                    tiempo_sostenido = ahora - tiempo_estable
                    tiempo_desde_ultimo = ahora - self._tiempo_ultimo

                    if tiempo_sostenido >= TIEMPO_PARA_CONFIRMAR and tiempo_desde_ultimo >= COOLDOWN:
                        self._ultimo_gesto = gesto
                        self._tiempo_ultimo = ahora
                        gesto_estable = None  # resetea para no repetir
                        tiempo_estable = None
                        self.cola.put(gesto)
                        print(f"[Cámara] Gesto confirmado: {gesto}")
            else:
                # Si no hay gesto, resetea el contador de estabilidad
                gesto_estable = None
                tiempo_estable = None

            cv2.imshow("Control por cámara - The Pibbles", frame_anotado)

            if cv2.waitKey(1) & 0xFF == ord('s'):
                self.camara_activa = False
                break

        cap.release()
        cv2.destroyAllWindows()
        self.camara_activa = False