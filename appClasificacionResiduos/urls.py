# appClasificacionResiduos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.clasificacion, name='clasificacion'),
    path('resultado/', views.resultado, name='resultado'),
]