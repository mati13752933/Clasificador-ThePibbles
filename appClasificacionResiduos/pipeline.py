import cv2
import numpy as np
import math

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
            total+=recorte[i][j][0]
    return int(total/(filas*cols))

def analizarImagen(imagen):#el main xd
    img = cv2.imread(imagen)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, np.array([0, 30, 30]), np.array([180, 255, 255]))
    contornos, basura = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #esto es lo que el inge no enseño, pero devuelve una lista las intersecciones de puntos negros y blancos
    #y se agarra el externo, por eso cv2.RETR_EXTERNAL, y cv2.CHAIN_APPROX_SIMPLE es en teoria 
    #por si tienes un rectngulo, que no te agarre toda la arista, solo los puntos(ya que un contorno
    #es una lista de listas de 2 que en [0] esta x, en [1] esta y, pero se guarda asi
    # [[[x,y]][[x1,y1]]] ), entonces se accede con doble [0][1][1] y aqui accedo al y1, esta topxd
    #por si acaso lo de basura es una wbda que genera, como la relacion que tienen, ponte cargas una lata 
    #con agujeros, te pone que el padre es el contorno de la lata y sus hijos son sus agujeros
    contorno=hallarMax(contornos)
    x,y,b,a=hallarBloque(contorno)
    area=hallarArea(contorno)
    perimetro=hallarPerimetro(contorno)
    ratio=round(b/a,2)
    circularidad=round((4*math.pi*area)/(perimetro**2),2)
    recorte=recortarCaja(hsv,x,y,b,a)
    promedio=hallarPromedioTono(recorte)

    #ya, mi idea final era mandarle este diccionario a la ia, y que en funcion a los datos lo
    #clasifique ella, espero que no falle, porque sino supongo que le voy a cargar las 200 fotos
    #eso lo hago mañana, cago de sueño zzz

    return{
        "tono Promedio":promedio,    
        "ratio":ratio,               
        "circularidad":circularidad, 
        "area":int(area)             
    }

def maincito(imagen):
    datosImagen=analizarImagen(imagen)
    promptcito = f'Clasificar:"Residuo" (tipo="texto", contexto="Métricas físicas de la muestra: {datosImagen}", restricciones="Identifica que objeto es y clasificalo en [Reciclable, No Reciclable, Aprovechable, Infeccioso], los daots que te doy son de un residuo sólido, devuelve SOLO la clasificacion")'
    tokenizador=Tokenizador()
    tokens=tokenizador.tokenizar(promptcito)
    parser=Parser(tokens)
    parseado=parser.parsear()
    constructorcito=PromptBuilder()
    promptFinal=constructorcito.construir(parseado)
    ia=Ia()
    res=ia.generar(promptFinal)
    return res