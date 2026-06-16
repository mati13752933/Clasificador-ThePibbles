from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .control_voz import ServicioVoz

servicio_voz = ServicioVoz()

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
    
    if comando == "detener":
        return redirect("detener_voz")
    resultado = comando["resultado"]

    return JsonResponse({
        "hay_comando": True,
        "texto": comando["texto"],
        "resultado": resultado
    })


