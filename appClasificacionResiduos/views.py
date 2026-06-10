from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .pipeline import maincito

def clasificacion(request):
    if request.method == "POST":
        imagen = request.FILES.get("imagen")

        if imagen:
            fs = FileSystemStorage(location="imagenes", base_url="/imagenes")
            nombre_archivo = fs.save(imagen.name, imagen)

            ruta_imagen = fs.path(nombre_archivo)
            imagen_url = fs.url(nombre_archivo)

            resultado_ia = str(maincito(ruta_imagen)).strip()
            print("el resultado es:", repr(resultado_ia))
            print("el resultado es: " + str(resultado_ia))

            mapa = {
                "1": "Reciclable",
                "2": "No Reciclable",
                "3": "Aprovechable",
                "4": "Infeccioso"
            }

            if resultado_ia in mapa:
                resultado = {
                    "ok": True,
                    "clasificacion": mapa[resultado_ia],
                    "datos": resultado_ia
                }
            else:
                resultado = {
                    "ok": False,
                    "error": f"Respuesta inválida de la IA: {resultado_ia}"
                }
            request.session["imagen_url"] = imagen_url
            request.session["resultado"] = resultado

            return redirect("resultado")
    return render(request, 'clasificacion.html')

def resultado(request):
    imagen_url = request.session.get("imagen_url")
    resultado = request.session.get("resultado")
    

    return render(request, 'clasificado.html', {"imagen_url": imagen_url, "resultado": resultado})
