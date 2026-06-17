import pyautogui
import cv2

def procesarGestoCamara(resultados_camara,datos_plantillas):
    if not resultados_camara or not datos_plantillas:
        return None
    contorno_camara=resultados_camara[0]["puntosContorno"]
    tono_camara=resultados_camara[0]["tonoPromedio"]
    menor_diferencia=float("inf")
    gestoGanador="ninguno"
    for ref in datos_plantillas:
        contorno_referencia=ref["puntosContorno"]
        tono_referencia=ref["tonoPromedio"]
        diferencia_tono=abs(tono_camara-tono_referencia)
        if diferencia_tono<=6:
            diferencia_silueta=cv2.matchShapes(contorno_camara,contorno_referencia,cv2.CONTOURS_MATCH_I1,0)
            penalizacion_color=diferencia_tono*0.05
            diferencia_total=diferencia_silueta+penalizacion_color
            if diferencia_total<menor_diferencia:
                menor_diferencia=diferencia_total
                gestoGanador=ref["tipoReferencia"]
    if menor_diferencia==float("inf"):
        return None
    similitud=max(0.0,round(100.0*(1.0-menor_diferencia),2))
    if similitud>=10:
        if gestoGanador=="derecha":
            pyautogui.move(15,0)
            print("derecha ",similitud)
        elif gestoGanador=="izquierda":
            pyautogui.move(-15,0)
            print("izquierda ",similitud)
        elif gestoGanador=="arriba":
            pyautogui.move(0,-15)
            print("arriba ",similitud)
        elif gestoGanador=="abajo":
            pyautogui.move(0,15)
            print("abajo ",similitud)
        elif gestoGanador=="palma":
            pyautogui.click()
            print("click",similitud)
            pyautogui.sleep(0.3) 
        return gestoGanador,similitud
    return None