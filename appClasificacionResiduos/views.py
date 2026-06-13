import base64
import cv2
import numpy as np
from django.shortcuts import render, redirect
from .pipeline import mainPrimeCompletoInsanoKaiokenSsj5
from django.contrib.auth.decorators import login_required 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def clasificacion(request):
    if request.method == "POST":
        imagen = request.FILES.get("imagen")
        if imagen:
            imagen_bytes = imagen.read()
            imagen.seek(0)
            np_arr = np.frombuffer(imagen_bytes, np.uint8)
            img_opencv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            resultado_ia = str(mainPrimeCompletoInsanoKaiokenSsj5(img_opencv, imagen)).strip()
            print("El objeto identificado es:", repr(resultado_ia))
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
            imagen_url = f"data:{imagen.content_type};base64,{imagen_base64}"
            resultado = {
                "ok": True,
                "clasificacion": resultado_ia,
            }
            request.session["imagen_url"] = imagen_url
            request.session["resultado"] = resultado
            return redirect("resultado")
    return render(request, 'clasificacion.html')

@login_required
def resultado(request):
    imagen_url = request.session.get("imagen_url")
    resultado = request.session.get("resultado")
    return render(request, 'clasificado.html', {"imagen_url": imagen_url, "resultado": resultado})
