# appClasificacionResiduos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.vista_reportes, name="reportes"),
    path("generar/", views.generar_reporte, name="generar_reporte"),
]