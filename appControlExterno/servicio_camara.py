import threading
import cv2
import os
from .funciones_camara import procesarGestoCamara
from appClasificacionResiduos.pipeline import analizarImagen

class ServicioCamara:
    def __init__(self):
        self.camara_activa = False
        self.hilo = None

    def iniciar(self):
        if not self.camara_activa:
            self.camara_activa = True
            self.hilo = threading.Thread(target=self._iniciar_camara, daemon=True)
            self.hilo.start()

    def detener(self):
        self.camara_activa = False

    def _iniciar_camara(self):
        baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpetaImagenes = os.path.join(baseDir, "imagenes")

        archivosGestos = {
            "derecha": "derecha.jpg",
            "izquierda": "izquierda.jpg",
            "arriba": "arriba.jpg",
            "abajo": "abajo.jpg",
            "palma": "circulo.jpg"
        }

        datos_plantillas = []

        for tipoGesto, nombreArchivo in archivosGestos.items():
            ruta = os.path.join(carpetaImagenes, nombreArchivo)

            if os.path.exists(ruta):
                analisis = analizarImagen(ruta)

                if analisis:
                    infoGesto = analisis[0]
                    infoGesto["tipoReferencia"] = tipoGesto
                    datos_plantillas.append(infoGesto)

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.camara_activa = False
            return

        while cap.isOpened() and self.camara_activa:
            ret, frame = cap.read()

            if not ret:
                break

            frame = cv2.flip(frame, 1)
            resultadosCamara = analizarImagen(frame)

            if resultadosCamara:
                resultadoGesto = procesarGestoCamara(resultadosCamara, datos_plantillas)

                if resultadoGesto:
                    gesto, porcentaje = resultadoGesto
                    infoTexto = f"Gesto: {gesto.upper()} ({porcentaje}%)"
                    cv2.putText(
                        frame,
                        infoTexto,
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

            cv2.imshow("Feed de la Camara - Proyecto The Pibbles", frame)

            if cv2.waitKey(1) & 0xFF == ord('s'):
                self.camara_activa = False
                break

        cap.release()
        cv2.destroyAllWindows()
        self.camara_activa = False


