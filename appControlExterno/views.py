from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
from Libreria.thepibbles.Audio.tts import Voz
import pyautogui
import time
from .estado_control import estado_archivo
from .control_voz import ServicioVoz
from .servicio_camara import ServicioCamara
import threading
import pygetwindow as gw

servicio_voz = ServicioVoz()
servicio_camara = ServicioCamara()
@login_required
def iniciar_voz(request):
    servicio_voz.iniciar()
    return JsonResponse({
        "ok": True,
        "escuchando": servicio_voz.escuchando,
        "mensaje": "Escucha activada."
    })

@login_required
def detener_voz(request):
    servicio_voz.detener()
    return JsonResponse({
        "ok": True,
        "escuchando": servicio_voz.escuchando,
        "mensaje": "Se detuvo la escucha."
    })

@login_required
def ejecutar_comando_voz(request):
    comando = servicio_voz.obtener_siguiente_comando()

    if comando is None:
        return JsonResponse({"hay_comando": False})

    resultado = comando["resultado"]

    if resultado.get("accion") == "detener":
        return redirect("detener_voz")

    return JsonResponse({
        "hay_comando": True,
        "texto": comando["texto"],
        "resultado": resultado
    })

@login_required
def estado_voz(request):
    return JsonResponse({
        "escuchando": servicio_voz.escuchando
    })

@login_required
def estado_camara(request):
    return JsonResponse({
        "activo": servicio_camara.camara_activa
    })

@login_required
def iniciar_camara(request):
    servicio_camara.iniciar()
    return JsonResponse({
        "ok": True,
        "activo": servicio_camara.camara_activa
    })

@login_required
def detener_camara(request):
    servicio_camara.detener()
    return JsonResponse({
        "ok": True,
        "activo": servicio_camara.camara_activa
    })

@login_required
def ejecutar_comando_camara(request):
    if not servicio_camara.camara_activa:
        return JsonResponse({"activo": False, "hay_gesto": False})

    resultado = servicio_camara.obtener_siguiente_gesto()

    if resultado is None:
        return JsonResponse({"activo": True, "hay_gesto": False})

    
    accion = resultado.get("accion")

    if accion == "detener_camara":
        gesto = "detener"
    elif accion == "redirigir":
        ruta = resultado.get("ruta", "")
        if ruta == "/":
            gesto = "inicio"
        elif "/clasificacion/" in ruta:
            gesto = "clasificacion"
        elif "/reportes/" in ruta:
            gesto = "reportes"
        elif "/perfil/" in ruta:
            gesto = "perfil"
        else:
            gesto = "desconocido"
    elif accion == "abrir_selector_imagen":
        gesto = "click"
    elif accion == "mensaje":
        return JsonResponse({"activo": True, "hay_gesto": False})
    else:
        return JsonResponse({"activo": True, "hay_gesto": False})

    return JsonResponse({
        "activo": True,
        "hay_gesto": True,
        "gesto": gesto
    })

@login_required
def cerrar_sesion_voz(request):
    logout(request)
    servicio_voz.detener()
    return redirect("inicio")

@login_required
def hablar_mensaje(request):
    texto = request.GET.get("texto")
    voz = Voz()
    audio = voz.volver_audio(texto)
    return HttpResponse(audio.getvalue(), content_type="audio/mpeg")

@login_required
def click_subir_imagen(request):
    try:
        x = int(float(request.GET.get("x")))
        y = int(float(request.GET.get("y")))
        time.sleep(0.2)
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        return JsonResponse({"ok": True, "mensaje": "Click realizado en el botón de subir imagen."})
    except Exception as e:
        print("Error haciendo click con pyautogui:", e)
        return JsonResponse({"ok": False, "mensaje": "No se pudo hacer click en subir imagen."})

@login_required
def pausar_voz(request):
    servicio_voz.pausar()
    return JsonResponse({"ok": True})

@login_required
def reanudar_voz(request):
    servicio_voz.reanudar()
    return JsonResponse({"ok": True})

@login_required
def activar_modo_archivos(request):
    estado_archivo.activar()

    return JsonResponse({
        "ok": True,
        "modo_archivos": True,
        "archivo_actual": estado_archivo.archivo_actual,
        "mensaje": "Modo selección de archivo activado."
    })


@login_required
def desactivar_modo_archivos(request):
    estado_archivo.desactivar()

    return JsonResponse({
        "ok": True,
        "modo_archivos": False,
        "mensaje": "Modo selección de archivo desactivado."
    })

def posicionar_mouse_primer_archivo():
    try:
        
        time.sleep(2.2)

        ventana = gw.getActiveWindow()

        if ventana is None:
            print("[Archivos] No hay ventana activa")
            return

        print("[Archivos] Ventana activa:", ventana.title)

    
        x = ventana.left + 230
        y = ventana.top + 180

        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(1)
        pyautogui.click()


    except Exception as e:
        print("[Archivos] Error posicionando mouse:", e)

    finally:
        print("[Archivos] Hilo de posicionamiento finalizado")


@login_required
def preparar_selector_archivos(request):
    hilo = threading.Thread(
        target=posicionar_mouse_primer_archivo,
        daemon=True
    )
    hilo.start()
    
    return JsonResponse({
        "ok": True,
        "mensaje": "Preparando selector de archivos."
    })