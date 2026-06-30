from django.urls import path
from . import views

urlpatterns = [
    path('iniciar_voz/', views.iniciar_voz, name='iniciar_voz'),
    path('detener_voz/', views.detener_voz, name='detener_voz'),
    path("iniciar_camara/", views.iniciar_camara, name="iniciar_camara"),
    path("detener_camara/", views.detener_camara, name="detener_camara"),
    path("ejecutar_comando_voz/", views.ejecutar_comando_voz, name="ejecutar_comando_voz"),
    path("cerrar-sesion-voz/", views.cerrar_sesion_voz, name="cerrar_sesion_voz"),
    path("hablar/", views.hablar_mensaje, name="hablar_mensaje"),
    path("click/", views.click_subir_imagen, name="click"),
    path("pausar-voz/", views.pausar_voz, name="pausar_voz"),
    path("reanudar-voz/", views.reanudar_voz, name="reanudar_voz"),
    path("ejecutar_comando_camara/", views.ejecutar_comando_camara, name="ejecutar_comando_camara"),
    path("estado_voz/", views.estado_voz, name= "estado_voz"),
    path("estado_camara/", views.estado_camara, name = "estado_camara"),
    path("activar-modo-archivos/", views.activar_modo_archivos, name="activar_modo_archivos"),
    path("desactivar-modo-archivos/", views.desactivar_modo_archivos, name="desactivar_modo_archivos"),
    path("preparar-selector-archivos/", views.preparar_selector_archivos, name="preparar_selector_archivos"),
    ]