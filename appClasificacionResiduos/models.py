# appClasificacionResiduos/models.py

from django.db import models
from decimal import Decimal
from usuarios.models import Perfil

class RegistroClasificacion(models.Model):
    CLASIFICACIONES = [
        ("Reciclable", "Reciclable"),
        ("No Reciclable", "No Reciclable"),
        ("Aprovechable", "Aprovechable"),
        ("Infeccioso", "Infeccioso"),
    ]

    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name="clasificaciones"
    )

    clasificacion = models.CharField(max_length=50, choices=CLASIFICACIONES)
    tipo = models.CharField(max_length=100)
    utilidad = models.FloatField(default=0)

    cantidad = models.PositiveIntegerField(default=1)

    peso_unitario_kg = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    ingreso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    egreso = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.clasificacion}"
