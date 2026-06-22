from django.db import models
from usuarios.models import Perfil


class EstadisticaPerfil(models.Model):
    perfil = models.OneToOneField(
        Perfil,
        on_delete=models.CASCADE,
        related_name="estadistica_residuos"
    )

    total_residuos = models.PositiveIntegerField(default=0)

    reciclables = models.PositiveIntegerField(default=0)
    no_reciclables = models.PositiveIntegerField(default=0)
    aprovechables = models.PositiveIntegerField(default=0)
    infecciosos = models.PositiveIntegerField(default=0)

    ingreso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    egreso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Estadísticas de {self.perfil.usuario.username}"


class ReporteGenerado(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name="reportes_generados"
    )

    total_residuos = models.PositiveIntegerField(default=0)
    ingreso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    egreso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte de {self.perfil.usuario.username}"