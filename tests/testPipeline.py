import pytest
from appClasificacionResiduos.pipeline import maincito

def testBotellaPlastico():
    resultado = maincito("imagenes/botellaAgua.png")
    assert resultado == "Reciclable"
def testBotellaVidrio():
    resultado = maincito("imagenes/botellaVidrio.png")
    assert resultado == "Reciclable"
