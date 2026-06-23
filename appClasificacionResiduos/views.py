import ast
import base64
import json
import re
import cv2
import numpy as np
from django.shortcuts import render, redirect
from .pipeline import mainPrimeCompletoInsanoKaiokenSsj5
from django.contrib.auth.decorators import login_required 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from .models import RegistroClasificacion


def _parsear_candidato(texto):
    if texto is None:
        return {}

    if isinstance(texto, bytes):
        texto = texto.decode("utf-8", errors="ignore")

    if not isinstance(texto, str):
        texto = str(texto)

    texto = texto.strip()

    # Quita bloques con código si vienen como ```json ... ```
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.MULTILINE)
        texto = texto.strip()

    # 1) JSON directo válido
    for cargador in (json.loads, ast.literal_eval):
        try:
            datos = cargador(texto)
            if isinstance(datos, dict):
                return datos
            if isinstance(datos, list):
                for item in datos:
                    if isinstance(item, dict):
                        return item
        except (ValueError, SyntaxError, TypeError):
            continue

    # 2) Busca cualquier objeto JSON dentro del texto
    for match in re.finditer(r"\{.*?\}", texto, flags=re.DOTALL):
        candidato = match.group(0)
        for cargador in (json.loads, ast.literal_eval):
            try:
                datos = cargador(candidato)
                if isinstance(datos, dict):
                    return datos
                if isinstance(datos, list):
                    for item in datos:
                        if isinstance(item, dict):
                            return item
            except (ValueError, SyntaxError, TypeError):
                continue

    # 3) Si llega algo como clave: valor o clave = valor
    pares = re.findall(r'([A-Za-z_]+)\s*[:=]\s*"?([^,\n]+)"?', texto)
    if pares:
        return {clave.strip(): valor.strip().strip('"\'') for clave, valor in pares}

    return {}


def _normalizar_datos_json(respuesta):
    if respuesta is None:
        return {}

    # Si ya viene como diccionario, lo usamos directo
    if isinstance(respuesta, dict):
        # Si el diccionario trae una capa extra de envoltorio, buscamos adentro
        for clave in ("resultado", "data", "response", "payload", "content", "text"):
            if clave in respuesta and isinstance(respuesta[clave], (dict, list, str)):
                datos = _normalizar_datos_json(respuesta[clave])
                if datos:
                    return datos

        # Si ya trae los campos esperados, se devuelve tal cual
        if all(clave in respuesta for clave in ("clasificacion", "tipo", "utilidad")):
            return respuesta

        # Si trae al menos uno de esos campos, también se devuelve
        if any(clave in respuesta for clave in ("clasificacion", "tipo", "utilidad")):
            return respuesta

        # Si el diccionario viene con una clave de texto, la parseamos
        for valor in respuesta.values():
            if isinstance(valor, (str, bytes, dict, list)):
                datos = _normalizar_datos_json(valor)
                if datos:
                    return datos
        return {}

    if isinstance(respuesta, list):
        for item in respuesta:
            datos = _normalizar_datos_json(item)
            if datos:
                return datos
        return {}

    if isinstance(respuesta, (str, bytes)):
        return _parsear_candidato(respuesta)

    return {}


@login_required
def clasificacion(request):
    if request.method == "POST":
        imagen = request.FILES.get("imagen")
        if imagen:
            imagen_bytes = imagen.read()
            imagen.seek(0)
            np_arr = np.frombuffer(imagen_bytes, np.uint8)
            img_opencv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            respuesta_ia = mainPrimeCompletoInsanoKaiokenSsj5(img_opencv, imagen)
            print("Respuesta IA original:", repr(respuesta_ia))

            # La IA debería responder con JSON real; si llega como texto o con envoltorios,
            # aquí lo normalizamos para que el template siempre reciba un diccionario limpio.
            datos_ia = _normalizar_datos_json(respuesta_ia)
            if not datos_ia:
                datos_ia = {
                    "clasificacion": str(respuesta_ia).strip()
                }

            print("Respuesta IA original:", repr(respuesta_ia))
            print("Datos de IA normalizados:", datos_ia)
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
            imagen_url = f"data:{imagen.content_type};base64,{imagen_base64}"
            resultado = {"ok": True, **datos_ia}
            resultado = guardar_resultado(request, resultado)
            request.session["imagen_url"] = imagen_url
            request.session["resultado"] = resultado
            return redirect("resultado")
    return render(request, 'clasificacion.html')

@login_required
def resultado(request):
    imagen_url = request.session.get("imagen_url")
    resultado = request.session.get("resultado")
    return render(request, 'clasificado.html', {"imagen_url": imagen_url, "resultado": resultado})

def guardar_resultado(request, respuesta):
    perfil = request.user.perfil

    clasificacion = respuesta["clasificacion"]
    tipo = respuesta["tipo"]
    
    # Limpiamos utilidad para asegurarnos de que sea un número (float)
    try:
        utilidad_str = str(respuesta.get("utilidad", "0")).replace("%", "").strip()
        utilidad = float(utilidad_str)
    except Exception:
        utilidad = 0.0

    cantidad = 1

    # Obtenemos los valores estimados directamente de la IA con valores por defecto
    try:
        peso = Decimal(str(respuesta.get("peso_estimado_kg", "0.00")))
    except Exception:
        peso = Decimal("0.00")

    try:
        precio = Decimal(str(respuesta.get("precio_estimado_bs_kg", "0.00")))
    except Exception:
        precio = Decimal("0.00")

    # Calculamos el ingreso
    if clasificacion in ["Reciclable", "Aprovechable"]:
        ingreso = peso * precio * Decimal(cantidad)
    else:
        ingreso = Decimal("0.00")

    # Calculamos el egreso como el 15% del ingreso
    egreso = ingreso * Decimal("0.15")

    RegistroClasificacion.objects.create(
        perfil=perfil,
        tipo=tipo,
        clasificacion=clasificacion,
        cantidad=cantidad,
        utilidad=utilidad,
        peso_unitario_kg=peso,    
        ingreso=ingreso,
        egreso=egreso,
    )
    return respuesta