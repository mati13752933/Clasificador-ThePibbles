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

    # Pulgar (horizontal)
    if landmarks[4].x < landmarks[3].x:
        dedos.append(1)
    else:
        dedos.append(0)

    # Índice, medio, anular, meñique (vertical)
    puntas = [8, 12, 16, 20]
    bases  = [6, 10, 14, 18]
    for punta, base in zip(puntas, bases):
        if landmarks[punta].y < landmarks[base].y:
            dedos.append(1)
        else:
            dedos.append(0)

    return sum(dedos)


def detectar_gesto(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    resultado = landmarker.detect(mp_image)

    gesto = None

    if resultado.hand_landmarks:
        landmarks = resultado.hand_landmarks[0]
        dedos = contar_dedos_arriba(landmarks)

        if dedos == 0:
            gesto = "detener"
        elif dedos == 1:
            gesto = "clasificacion"
        elif dedos == 2:
            gesto = "reportes"
        elif dedos == 3:
            gesto = "perfil"
        elif dedos == 5:
            gesto = "click"

        if gesto:
            # Dibuja los puntos manualmente porque la API nueva es diferente
            h, w, _ = frame.shape
            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            cv2.putText(
                frame,
                f"Gesto: {gesto.upper()}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                2
            )

    return gesto, frame