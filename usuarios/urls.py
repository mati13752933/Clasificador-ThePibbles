from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.perfil, name='perfil'),
    path('editar/', views.editarPerfil, name='editar_perfil')
]