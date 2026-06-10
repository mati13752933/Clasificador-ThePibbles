
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('clasificacion/', include('appClasificacionResiduos.urls')),
    path('usuarios/', include('appAdministracionUsuarios.urls')),
    path('reportes/', include('appReportes.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
