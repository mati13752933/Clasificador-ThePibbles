import pytest
from appClasificacionResiduos.pipeline import maincito

def testBotellaPlastico():
    resultado = maincito("imagenes/botellaAgua.png")
    assert resultado == "1"
def testBotellaVidrio():
    resultado = maincito("imagenes/botellaVidrio.png")
    assert resultado == "1"
def testLataCocaCola():
    resultado = maincito("imagenes/lataCocaCola.png")
    assert resultado == "1"
    #Le ponemos numeros, porque la ia me dice cosas que no estan en las opciones o le mete "\n"
    #Y bueno, con los numeros no me dice nada raro(aunque sigue fallando) 

    #Nicol, esta horrible, a veces sí lo hace bien, luego hace una mrda
    #Ahora pienso ennnn cargar 200 imágenes de lo más común, y decirle a la ia:
    #Toma esta info(colorPromedio,ratio....) + creo que es x cosa (esa x cosa vamos a sacarlo
    #comparando la forma del contorno de la foto con las otras 200 fotos)
    #pero mas rato hago eso, voy a estuidar numerico y algo de la scesi