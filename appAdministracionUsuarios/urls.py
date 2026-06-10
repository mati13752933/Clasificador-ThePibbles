

from django.urls import path
from . import views

urlpatterns = [
    path('', views.adm, name='adm'),
]