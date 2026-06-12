import cv2
import numpy as np
import math
import heapq

import os
from Libreria.thepibbles.Gramatica.lexer import Tokenizador
from Libreria.thepibbles.Gramatica.parser import Parser
from Libreria.thepibbles.IA.promptBuilder import PromptBuilder
from Libreria.thepibbles.IA.ia import Ia

#Puse comentarios para que no sea todo un despute

def hallarArea(contorno):#Lit te halla el area de un poligono como en alg1(geo analitica)
    n=len(contorno)
    area=0
    for i in range(n):
        x1,y1=contorno[i][0]
        x2,y2=contorno[(i+1)%n][0]
        area+=(x1*y2)-(x2*y1)
    return abs(area)/2

def hallarPerimetro(contorno):#Te halla el perimetro con pitagoras
    n=len(contorno)
    res=0
    for i in range(n):
        x1,y1=contorno[i][0]
        x2,y2=contorno[(i+1)%n][0]
        rx=x2-x1
        ry=y2-y1
        res+=(rx**2+ry**2)**0.5
    return res

def hallarMax(contornos):#De todos los contornos, te da el de mayor area
    mejor=0
    res=contornos[0]
    for i in contornos:
        if mejor<hallarArea(i):
            res=i
            mejor=hallarArea(i)
    return res

def hallarBloque(contorno):#Te da el bloquecito(margen), como en el ejemplo de la cara
    listaX=[]
    listaY=[]
    for i in contorno:
        coordx=i[0][0]
        coordy=i[0][1]
        listaX.append(coordx)
        listaY.append(coordy)
    x=min(listaX)
    y=min(listaY)
    b=max(listaX)-x
    a=max(listaY)-y
    return x,y,b,a

def recortarCaja(hsv,x,y,b,a):#Te recorta el bloquecito, solo te quedas con lo de adentro
    recorte=[]
    for i in range(y,y+a):
        nueva_fila=[]
        for j in range(x,x+b):
            pixel=hsv[i][j]
            nueva_fila.append(pixel)
        recorte.append(nueva_fila)
    return recorte

def hallarPromedioTono(recorte):#Entre los tonos del recorte(solo el objeto) te da el tono promedio
    total=0
    filas=len(recorte)
    cols=len(recorte[0])
    for i in range(filas):
        for j in range(cols):
            total+=int(recorte[i][j][0])
    return int(total/(filas*cols))

def comparar(listaRecortes):
    baseDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #da la rutaa a la base del proyceto
    carpetaImagenes=os.path.join(baseDir, "imagenes")#genera la ruta hasta la carpeta donde estna las imagnes
    archivosObjetos=[
        "botellaPlastico1.png",
        "botellaPlastico2.jpeg",
        "botellaPlastico3.png",
        "botellaVidrio1.png",
        "cajaCarton1.png",
        "cascaraFruta1.jpg",
        "cascaraFruta2.jpg",
        "cascaraFruta3.jpg",
        "cigarro1.png",
        "jeringa1.png",
        "jeringa2.png",
        "lata1.jpg",
        "lata2.png",
        "panial1.png",
        "gasa1.png"
    ]
    datosObjetos=[]    
    for nombreArchivo in archivosObjetos:
        ruta=os.path.join(carpetaImagenes, nombreArchivo)#solo crea la ruta
        if os.path.exists(ruta):
            analisis=analizarImagen(ruta)
            if analisis:#todo lo demas se enteidne xd
                infoObjeto=analisis[0]
                if "lata" in nombreArchivo.lower():
                    tipoPredicho="lata"
                elif "plastico" in nombreArchivo.lower() or "plastico" in nombreArchivo.lower():
                    tipoPredicho="botella de plástico"
                elif "vidrio" in nombreArchivo.lower():
                    tipoPredicho="botella de vidrio"
                elif "carton" in nombreArchivo.lower():
                    tipoPredicho="caja de cartón"
                elif "cascara" in nombreArchivo.lower():
                    tipoPredicho="cáscara de fruta"
                elif "cigarro" in nombreArchivo.lower():
                    tipoPredicho="colilla de cigarro"
                elif "jeringa" in nombreArchivo.lower():
                    tipoPredicho="jeringa médica"
                elif "panial" in nombreArchivo.lower():
                    tipoPredicho="pañal usado"
                elif "gasa" in nombreArchivo.lower():
                    tipoPredicho="gasa hospitalaria"
                else:
                    tipoPredicho="residuo"                    
                infoObjeto["tipoReferencia"]=tipoPredicho
                datosObjetos.append(infoObjeto)
    for obj in listaRecortes:
        maxSimilitud=0.0
        tipoGanador="objeto desconocido"
        for ref in datosObjetos:
            if ref["ratio"]>0:
                difRatio=abs(obj["ratio"]-ref["ratio"])/(ref["ratio"])
            else:
                difRatio=abs(obj["ratio"]-ref["ratio"])/1
            if ref["circularidad"]>0:
                difCirc=abs(obj["circularidad"]-ref["circularidad"])/(ref["circularidad"])
            else:
                difCirc=abs(obj["circularidad"]-ref["circularidad"])/1
            difTono=abs(obj["tonoPromedio"]-ref["tonoPromedio"])/180.0
            if ref["area"]>0:
                difArea=abs(obj["area"]-ref["area"])/(ref["area"])
            else:
                difArea=abs(obj["area"]-ref["area"])/1
            distancia=(difRatio*0.3)+(difCirc*0.3)+(difTono*0.2)+(difArea*0.2)
            similitud=max(0.0,100.0*(1.0-distancia))
            if similitud>maxSimilitud:
                maxSimilitud=similitud
                tipoGanador=ref["tipoReferencia"]
        obj["similtudReferencia"] = round(maxSimilitud, 2)
        obj["tipoClasificado"] = tipoGanador
    return listaRecortes

#Explicacion xdd
def analizarImagen(imagen):

    if isinstance(imagen, str):# Si es una ruta de texto (las referencias)
            img = cv2.imread(imagen)
    else:# Si ya es la matriz de pixeles de Django
            img = imagen
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)#lo vuelve emo (negro, gris y blacno)
    difuminado = cv2.GaussianBlur(gris, (5, 5), 0)#elimina ruido pequeño de pixeles
    bordes = cv2.Canny(difuminado, 30, 150)#saca todos los bordes
    grosor = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))#genera el grosor
    mascaraCerrada = cv2.morphologyEx(bordes, cv2.MORPH_CLOSE, grosor)#cierra grietas engordando y luego vuelve
    contornosBordes, _ = cv2.findContours(mascaraCerrada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#lista de listas de cc
    mascaraFinal = np.zeros_like(gris)#genera una imagen negra del mismo tamaño
    cv2.drawContours(mascaraFinal, contornosBordes, -1, (255), thickness=cv2.FILLED)#Dibuja en la imagen negra los contornos
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    contornos, basura = cv2.findContours(mascaraFinal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#saca otra vez, pero ya es imagen limpia
    colaPrioridad=[]
    for i in range(len(contornos)):
        contorno = contornos[i]
        area = hallarArea(contorno)
        if area > 500:#si es muy pequeña no entra, pq seguro es basura
            heapq.heappush(colaPrioridad, (-area, i, contorno))
    listaRecortes = []
    while colaPrioridad:
        areaNegativa, pos, contornoActual = heapq.heappop(colaPrioridad)
        areaReal = abs(areaNegativa)
        x, y, b, a = hallarBloque(contornoActual)
        perimetro = hallarPerimetro(contornoActual)
        ratio = round(b / a, 2)
        circularidad = round((4 * math.pi * areaReal) / (perimetro ** 2), 2)
        recorte = recortarCaja(hsv, x, y, b, a)
        promedio = hallarPromedioTono(recorte)
        listaRecortes.append({
            "objetoId": len(listaRecortes) + 1,
            "tonoPromedio": promedio,    
            "ratio": ratio,               
            "circularidad": circularidad, 
            "area": int(areaReal),
            "coordenadasCaja": (x, y, b, a),
            "puntosContorno": contornoActual
        })
    return listaRecortes


def mainPrimeCompletoInsanoKaiokenSsj5(imagen, archivo_bytes):
    listita = analizarImagen(imagen)
    listita = comparar(listita)
    objetoPrincipal=listita[0]
    porcentaje=objetoPrincipal["similtudReferencia"]
    tipoObjeto=objetoPrincipal["tipoClasificado"]
    promptcito={"accion": "Clasificar", "tema": "Residuos", "parametros": {"tipo": "texto", "contexto": f"Eres un Clasificador de residuos. El algoritmo de visión artificial determinó que el objeto principal analizado geométricamente tiene un {porcentaje}% de similitud matemática con una '{tipoObjeto}'. Utiliza este dato junto con la imagen para clasificar con precisión.", "restricciones": "Clasifica el tipo de residuo que es, tiene que ser uno de estos: [Reciclable, No Reciclable, Aprovechable, Infeccioso]. Responde ÚNICAMENTE la clasificación."}}
    constructorcito=PromptBuilder()
    promptFinal =constructorcito.construir(promptcito)
    ia = Ia()
    res=ia.generarConImagen(archivo_bytes.read(), archivo_bytes.content_type, promptFinal)
    return res











#para LEITO
def identificarImagen(imagen):
    promptcito = {"accion": "Identificar", "tema": "Residuos", "parametros": {"tipo": "texto", "contexto": "Eres un Identificador de residuos (plástico, lata, papel, madera, vidrio, carton, cáscaras de frutas, etc...)", "restricciones": "Identifica el tipo de residuo que es, entre estas opciones: [plastico, papel, lata, madera, vidrio, cascara, carton, LO QUE VEAS LEITOxd]"}}
    constructorcito = PromptBuilder()
    prompt_final = constructorcito.construir(promptcito)
    ia = Ia()
    res = ia.generarConImagen(imagen.read(), imagen.content_type, prompt_final)
    return res