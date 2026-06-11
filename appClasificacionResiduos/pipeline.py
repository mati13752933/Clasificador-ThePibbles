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

def analizarImagen(imagen):
    img = cv2.imread(imagen)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, np.array([0, 30, 30]), np.array([180, 255, 255]))
    contornos, basura = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    colaPrioridad = []
    for i in range(len(contornos)):
        contorno = contornos[i]
        area = hallarArea(contorno)
        if area > 500:
            heapq.heappush(colaPrioridad, (-area, i, contorno))
    listaRecortes = []
    while colaPrioridad:
        areaNegativa,pos, contornoActual = heapq.heappop(colaPrioridad)
        areaReal = abs(areaNegativa)
        x, y, b, a = hallarBloque(contornoActual)
        perimetro = hallarPerimetro(contornoActual)
        ratio = round(b / a, 2) if a != 0 else 0
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


#Ahora mandando imagen a la ia
def maincitoImagenDirecta(imagen):
    promptcito = {"accion": "Clasificar", "tema": "Residuos", "parametros": {"tipo": "texto", "contexto": "Eres un Clasificador de residuos (plástico, lata, papel, madera, vidrio, carton, cáscaras de frutas, etc...)", "restricciones": "Clasifica el tipo de residuo que es, tiene que ser uno de estos: [Reciclable, No Reciclable, Aprovechable, Infeccioso], debes responder SOLO CON LA CLASIFICACION, no dar explicaciones ni nada"}}
    constructorcito = PromptBuilder()
    prompt_final = constructorcito.construir(promptcito)
    ia = Ia()
    res = ia.generarConImagen(imagen.read(), imagen.content_type, prompt_final)
    return res
        
#para LEITO
def identificarImagen(imagen):
    promptcito = {"accion": "Identificar", "tema": "Residuos", "parametros": {"tipo": "texto", "contexto": "Eres un Identificador de residuos (plástico, lata, papel, madera, vidrio, carton, cáscaras de frutas, etc...)", "restricciones": "Identifica el tipo de residuo que es, entre estas opciones: [plastico, papel, lata, madera, vidrio, cascara, carton, LO QUE VEAS LEITOxd]"}}
    constructorcito = PromptBuilder()
    prompt_final = constructorcito.construir(promptcito)
    ia = Ia()
    res = ia.generarConImagen(imagen.read(), imagen.content_type, prompt_final)
    return res
        
