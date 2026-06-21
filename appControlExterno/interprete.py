import unicodedata

CONECTORES = [" y ", " luego ", " despues ", " después ", " tambien ", " también "]

VERBOS = {
    "ir": [
        "ir", "ve", "anda", "dirigete", "dirígete", "llevarme",
        "navegar", "entrar", "acceder", "abrir", "abre", "mostrar", "muestra", "entra", "volver", "vuelve"
    ],
    "clasificar": [
        "clasificar", "analizar", "procesar", "evaluar", "revisar",
        "identificar", "detectar"
    ],
    "cargar": [
        "subir", "cargar", "adjuntar", "seleccionar", "elegir", "elige", "carga", "adjunta", "elegir"
    ],
    "ayuda": [
        "ayuda", "ayudame", "ayúdame", "instrucciones", "explica"
    ],

    "detener" : [
        "detener", "para", "parar", "detente", "alto", "stop"
    ],

    "editar" : [
        "editar", "cambiar", "personalizar"
    ],

    "cerrar": [
        "cerrar", "close", "terminar", "acabar", "cierra", "termina", "terminando", "acaba", "sal", "salir"
    ]

}


OBJETOS = {
    "inicio": [
        "inicio", "home", "principal", "pagina principal", "página principal"
    ],
    "clasificacion": [
        "clasificacion", "clasificación", "clasificador", "residuos",
        "residuo"
    ],
    "reportes": [
        "reportes", "reporte", "estadisticas", "estadísticas",
        "historial", "resultados"
    ],

    "perfil": [
        "perfil", "mi perfil", "usuario", "cuenta"
    ],
    "imagen":[
        "imagen", "foto", "foto de residuo", "foto del residuo", "archivo"
    ],
    "camara" : [
        "cámara", "video"
    ],

    "sesion": [
        "sesion", "cuenta"
    ]
}


def normalizar(texto):
    if texto is None:
        return ""

    texto = texto.lower().strip()

    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

    return texto


def buscar_grupo(texto, diccionario):
    texto = normalizar(texto)

    for grupo, palabras in diccionario.items():
        for palabra in palabras:
            palabra = normalizar(palabra)

            if palabra in texto:
                return grupo

    return None

def dividir_comandos(texto):
    texto = normalizar(texto)

    partes = [texto]

    for conector in CONECTORES:
        nuevas_partes = []

        for parte in partes:
            nuevas_partes.extend(parte.split(conector))

        partes = nuevas_partes

    return [p.strip() for p in partes if p.strip()]

def interpretar_comando(texto):
    texto_limpio = normalizar(texto)

    if texto_limpio == "":
        return {
            "ok": False,
            "accion": "desconocido",
            "mensaje": "No se detectó ningún comando."
        }
    
    verbo = buscar_grupo(texto_limpio, VERBOS)
    objeto = buscar_grupo(texto_limpio, OBJETOS)

    print("ANTES DE IF CONTROL:", verbo, objeto)
    if verbo == "ayuda":
        return {
            "ok": True,
            "accion": "mensaje",
            "mensaje": "Puedes decir: abrir clasificación, ir a reportes, abrir administración, ir a perfil o volver al inicio."
        }
    
    if verbo == "detener" :
        return {
            "ok": True,
            "accion": "detener",
            "mensaje": "Se termino el control por voz."
        }

    if verbo is None:
        return {
            "ok": False,
            "accion": "desconocido",
            "texto": texto,
            "mensaje": "No entendí qué acción quieres realizar."
        }

    if objeto is None:
        return {
            "ok": False,
            "accion": "desconocido",
            "texto": texto,
            "mensaje": "Entendí la acción, pero no entendí a qué módulo quieres ir."
        }

    if verbo in ["ir" ] and objeto == "clasificacion":
        return {
            "ok": True,
            "accion": "redirigir",
            "ruta": "/clasificacion/",
            "mensaje": "Abriendo clasificación."
        }

    if verbo == "ir" and objeto == "inicio":
        return {
            "ok": True,
            "accion": "redirigir",
            "ruta": "/",
            "mensaje": "Volviendo al inicio."
        }

    if verbo == "ir" and objeto == "reportes":
        return {
            "ok": True,
            "accion": "redirigir",
            "ruta": "/reportes/",
            "mensaje": "Abriendo reportes."
        }
  
    if verbo == "ir" and objeto == "perfil":
        return {
            "ok": True,
            "accion": "redirigir",
            "ruta": "/perfil/",
            "mensaje": "Abriendo perfil."
        }
    
    if verbo == "editar" and objeto == "perfil":
        return {
            "ok": True,
            "accion": "redirigir",
            "ruta": "/perfil/editar/",
            "mensaje": "Abriendo opcion para editar perfil."
        }

    if verbo in ["ir", "cargar"] and objeto == "imagen":
        return{
            "ok":True,
            "accion": "abrir_selector_imagen",
            "ruta": "/clasificacion/?accion=subir_imagen",
            "mensaje": "Abriendo selector de imagen."
        }
    
        
    if verbo == "cerrar" and objeto == "sesion":
        return {
            "ok": True,
            "accion": "redirigir",
            "ruta": "/control/cerrar-sesion-voz/",
            "mensaje": "Cerrando sesión."
        } 
        
    return {
        "ok": False,
        "accion": "desconocido",
        "texto": texto,
        "mensaje": f"Entendí '{verbo}' y '{objeto}', pero no tengo esa acción configurada."
    }