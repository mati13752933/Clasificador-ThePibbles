from django.urls import path
from . import views

urlpatterns = [
    path('', views.control_voz, name='control_voz'),
    path('iniciar_voz/', views.iniciar_voz, name='iniciar_voz'),
    path('detener_voz/', views.detener_voz, name='detener_voz'),
    path('ejecutar_comando_voz/', views.ejecutar_comando_voz, name='ejecutar_comando_voz'),
]