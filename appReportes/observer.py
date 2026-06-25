# appReportes/observer.py

import sys
from decimal import Decimal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from appClasificacionResiduos.models import RegistroClasificacion
from .models import EstadisticaPerfil


class ClasificacionObserver:
    
    def update(self, registro):
        perfil = registro.perfil

        perfil.residuos_clasificados += registro.cantidad
        perfil.save()

        estadistica, _ = EstadisticaPerfil.objects.get_or_create(
            perfil=perfil
        )

        estadistica.total_residuos += registro.cantidad
        estadistica.ingreso_total += registro.ingreso
        estadistica.egreso_total += registro.egreso

        if registro.clasificacion == "Reciclable":
            estadistica.reciclables += registro.cantidad

        elif registro.clasificacion == "No Reciclable":
            estadistica.no_reciclables += registro.cantidad

        elif registro.clasificacion == "Aprovechable":
            estadistica.aprovechables += registro.cantidad

        elif registro.clasificacion == "Infeccioso":
            estadistica.infecciosos += registro.cantidad


        estadistica.save()


@receiver(pre_save, sender=RegistroClasificacion)
def ajustar_valores_registro(sender, instance, **kwargs):
    frame = sys._getframe()
    respuesta = None
    while frame:
        if frame.f_code.co_name == 'guardar_resultado':
            respuesta = frame.f_locals.get('respuesta')
            break
        frame = frame.f_back

    if respuesta:
        try:
            cantidad = int(respuesta.get("cantidad", 1))
            if cantidad < 1:
                cantidad = 1
        except Exception:
            cantidad = 1

        try:
            utilidad_str = str(respuesta.get("utilidad", "0")).replace("%", "").strip()
            utilidad = float(utilidad_str)
        except Exception:
            utilidad = 0.0

        try:
            peso = Decimal(str(respuesta.get("peso_estimado_kg", "0.00")))
        except Exception:
            peso = Decimal("0.00")

        try:
            precio = Decimal(str(respuesta.get("precio_estimado_bs_kg", "0.00")))
        except Exception:
            precio = Decimal("0.00")

        clasif = instance.clasificacion
        if clasif in ["Infeccioso", "No Reciclable"]:
            ingreso = Decimal("0.00")
            egreso = Decimal("6.70") * peso * Decimal(cantidad)
        elif clasif in ["Reciclable", "Aprovechable"]:
            ingreso = peso * precio * Decimal(cantidad)
            egreso = ingreso * Decimal("0.13")
        else:
            ingreso = Decimal("0.00")
            egreso = Decimal("0.00")

        instance.cantidad = cantidad
        instance.utilidad = utilidad
        instance.peso_unitario_kg = peso
        instance.ingreso = ingreso
        instance.egreso = egreso


@receiver(post_save, sender=RegistroClasificacion)
def notificar_observer_clasificacion(sender, instance, created, **kwargs):
    if created:
        observer = ClasificacionObserver()
        observer.update(instance)