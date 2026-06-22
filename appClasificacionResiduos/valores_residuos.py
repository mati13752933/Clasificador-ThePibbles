from decimal import Decimal
import unicodedata


VALORES_MATERIALES = {
    "plastico": {
        "peso_promedio_kg": Decimal("0.030"),
        "precio_bs_kg": Decimal("1.80"),
    },
    "carton": {
        "peso_promedio_kg": Decimal("0.100"),
        "precio_bs_kg": Decimal("0.50"),
    },
    "papel": {
        "peso_promedio_kg": Decimal("0.020"),
        "precio_bs_kg": Decimal("1.00"),
    },
    "vidrio": {
        "peso_promedio_kg": Decimal("0.250"),
        "precio_bs_kg": Decimal("0.15"),
    },
    "aluminio": {
        "peso_promedio_kg": Decimal("0.015"),
        "precio_bs_kg": Decimal("6.50"),
    },
    "metal": {
        "peso_promedio_kg": Decimal("0.100"),
        "precio_bs_kg": Decimal("2.00"),
    },
    "electronico": {
        "peso_promedio_kg": Decimal("0.300"),
        "precio_bs_kg": Decimal("0.00"),
    },
    "cascara": {
        "peso_promedio_kg": Decimal("0.050"),
        "precio_bs_kg": Decimal("0.00"),
    },
}


def normalizar_texto(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto


def obtener_tipo(tipo):
    tipo = normalizar_texto(tipo)

    if tipo == "plastico":
        return "plastico"

    if tipo == "carton":
        return "carton"

    if tipo == "papel":
        return "papel"

    if tipo == "vidrio":
        return "vidrio"

    if tipo == "alumnio":
        return "aluminio"

    if tipo == "metal":
        return "metal"

    if tipo == "electronico":
        return "electronico"
    
    if tipo == "cascara":
        return "cascara"

    return "desconocido"

def calcular_valores_residuo(tipo, clasificacion, cantidad=1):
    material = obtener_tipo(tipo)

    if material not in VALORES_MATERIALES:
        # Devolvemos 3 valores en el orden correcto: ingreso, peso, precio
        return Decimal("0.00"), Decimal("0.000"), Decimal("0.00")

    datos = VALORES_MATERIALES[material]

    peso = datos["peso_promedio_kg"]
    precio = datos["precio_bs_kg"]

    if clasificacion in ["Reciclable", "Aprovechable"]:
        ingreso = peso * precio * Decimal(cantidad)
    else:
        ingreso = Decimal("0.00")

    # Devolvemos los 3 valores que views.py intenta desempaquetar
    return ingreso, peso, precio