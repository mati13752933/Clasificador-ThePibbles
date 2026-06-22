from django.shortcuts import render, redirect
from appClasificacionResiduos.models import RegistroClasificacion
from .models import EstadisticaPerfil, ReporteGenerado
from django.contrib.auth.decorators import login_required 

@login_required
def generar_reporte(request):
    if request.method == "POST":
        perfil = request.user.perfil

        estadistica, _ = EstadisticaPerfil.objects.get_or_create(
            perfil=perfil
        )

        ReporteGenerado.objects.create(
            perfil=perfil,
            total_residuos=estadistica.total_residuos,
            ingreso_total=estadistica.ingreso_total,
            egreso_total=estadistica.egreso_total
        )

        return redirect("/reportes/?generado=1")

    return redirect("reportes")

@login_required
def vista_reportes(request):
    perfil = request.user.perfil

    registros = RegistroClasificacion.objects.filter(
        perfil=perfil
    ).order_by("-fecha")

    estadistica, _ = EstadisticaPerfil.objects.get_or_create(
        perfil=perfil
    )

    total_reportes = ReporteGenerado.objects.filter(
        perfil=perfil
    ).count()

    ultimo_reporte = ReporteGenerado.objects.filter(
        perfil=perfil
    ).order_by("-fecha_generacion").first()

    return render(request, "reportes.html", {
        "registros": registros,
        "estadistica": estadistica,
        "total_reportes": total_reportes,
        "ultimo_reporte": ultimo_reporte,
    })