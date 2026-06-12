import base64
from django.shortcuts import render, redirect
from .pipeline import maincitoImagenDirecta
from django.contrib.auth.decorators import login_required 

@login_required
def clasificacion(request):
    if request.method == "POST":
        imagen = request.FILES.get("imagen")
        if imagen:
            resultado_ia = str(maincitoImagenDirecta(imagen)).strip()
            print("El objeto identificado es:", repr(resultado_ia))
            imagen.seek(0) 
            imagen_bytes = imagen.read()
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
