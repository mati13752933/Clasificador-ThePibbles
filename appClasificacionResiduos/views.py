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

            resultado = maincito(ruta_imagen)
            print("el resultado es: " + str(resultado))

            request.session["imagen_url"] = imagen_url
            request.session["resultado"] = resultado

            return redirect("resultado")
    return render(request, 'clasificacion.html')

def resultado(request):
    imagen_url = request.session.get("imagen_url")
    resultado = request.session.get("resultado")
    

    return render(request, 'clasificado.html', {"imagen_url": imagen_url, "resultado": resultado})
