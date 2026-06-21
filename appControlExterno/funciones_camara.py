import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

BaseOptions = mp_python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

landmarker = HandLandmarker.create_from_options(options)


def contar_dedos_arriba(landmarks):
    dedos = []

    if landmarks[4].x < landmarks[3].x:
        dedos.append(1)
    else:
        dedos.append(0)

    puntas = [8, 12, 16, 20]
    bases  = [6, 10, 14, 18]
    for punta, base in zip(puntas, bases):
        if landmarks[punta].y < landmarks[base].y:
            dedos.append(1)
        else:
            dedos.append(0)

    return sum(dedos)


GESTOS_NAVEGACION = {
    0: "detener",
    1: "inicio",
    2: "clasificacion",
    3: "reportes",
    4: "perfil",
    5: "subir_imagen",
}

GESTOS_ARCHIVOS = {
    1: "archivo_subir",
    2: "archivo_bajar",
    3: "archivo_cerrar",
    5: "archivo_seleccionar",
}

ETIQUETAS_PANTALLA = {
    "detener":            "PUÑO - Detener camara",
    "inicio":             "1 - Inicio",
    "clasificacion":      "2 - Clasificacion",
    "reportes":           "3 - Reportes",
    "perfil":             "4 - Perfil",
    "subir_imagen":       "5 - Subir imagen",
    "archivo_subir":      "1 - Subir",
    "archivo_bajar":      "2 - Bajar",
    "archivo_cerrar":     "3 - Cerrar selector",
    "archivo_seleccionar":"5 - Seleccionar archivo",
}


def detectar_gesto(frame, modo_archivos=False):
    """
    Detecta el gesto de la mano en el frame.

    Parámetros:
        frame        -- frame BGR de OpenCV
        modo_archivos -- True si el selector de archivos está abierto

    Retorna:
        (gesto, frame_anotado)
        gesto es un string o None si no se detecta nada reconocido.
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    resultado = landmarker.detect(mp_image)

    gesto = None

    if resultado.hand_landmarks:
        landmarks = resultado.hand_landmarks[0]
        dedos = contar_dedos_arriba(landmarks)

        
        if modo_archivos:
            gesto = GESTOS_ARCHIVOS.get(dedos)
        else:
            gesto = GESTOS_NAVEGACION.get(dedos)

        h, w, _ = frame.shape
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        if gesto:
            etiqueta = ETIQUETAS_PANTALLA.get(gesto, gesto.upper())
            cv2.putText(
                frame,
                etiqueta,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )
        else:
            
            cv2.putText(
                frame,
                f"{dedos} dedos - sin accion",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 165, 255),
                2
            )

    return gesto, frame