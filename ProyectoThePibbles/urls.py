
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view( template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('clasificacion/', include('appClasificacionResiduos.urls')),
    path('usuarios/', include('appAdministracionUsuarios.urls')),
    path('reportes/', include('appReportes.urls')),
    path('perfil/', include('usuarios.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
