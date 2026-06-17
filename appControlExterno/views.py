from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from Libreria.thepibbles.Audio.tts import Voz
from django.http import HttpResponse
import pyautogui
import time

from .control_voz import ServicioVoz
from .servicio_camara import ServicioCamara

servicio_voz = ServicioVoz()
servicio_camara = ServicioCamara()

@login_required
def control_voz(request):
    return render(request, "control.html", {
        "escuchando": servicio_voz.escuchando
    })


@login_required
def iniciar_voz(request):
    servicio_voz.iniciar()
    return redirect("control_voz")


@login_required
def detener_voz(request):
    servicio_voz.detener()
    return redirect("control_voz")
    


@login_required
def ejecutar_comando_voz(request):
    comando = servicio_voz.obtener_siguiente_comando()

    if comando is None:
        return JsonResponse({
            "hay_comando": False
        })
    
    
    resultado = comando["resultado"]
    
    if resultado.get("accion") == "detener":
        return redirect("detener_voz")

    return JsonResponse({
        "hay_comando": True,
        "texto": comando["texto"],
        "resultado": resultado
    })

@login_required
def iniciar_camara(request):
    servicio_camara.iniciar()
    return redirect("control_voz")


@login_required
def detener_camara(request):
    servicio_camara.detener()
    return redirect("control_voz")

@login_required
def cerrar_sesion_voz(request):
    logout(request)
    servicio_voz.detener()
    return redirect("inicio")

@login_required
def hablar_mensaje(request):
    texto = request.GET.get("texto", "Comando ejecutado.")

    voz = Voz()
    audio = voz.volver_audio(texto) 

    return HttpResponse(
        audio.getvalue(),
        content_type="audio/mpeg"
    )

@login_required
def click_subir_imagen(request):
    try:
        x = int(float(request.GET.get("x")))
        y = int(float(request.GET.get("y")))

        time.sleep(0.2)

        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()

        return JsonResponse({
            "ok": True,
            "mensaje": "Click realizado en el botón de subir imagen."
        })

    except Exception as e:
        print("Error haciendo click con pyautogui:", e)

        return JsonResponse({
            "ok": False,
            "mensaje": "No se pudo hacer click en subir imagen."
        })
    
@login_required
def pausar_voz(request):
    servicio_voz.pausar()
    return JsonResponse({"ok": True})


@login_required
def reanudar_voz(request):
    servicio_voz.reanudar()
    return JsonResponse({"ok": True})
