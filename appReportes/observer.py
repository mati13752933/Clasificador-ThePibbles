# appReportes/observer.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from appClasificacionResiduos.models import RegistroClasificacion
from .models import EstadisticaPerfil


class ClasificacionObserver:
    """
    Observer que actualiza el perfil y las estadísticas
    cuando se crea un nuevo RegistroClasificacion.
    """

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

        elif registro.clasificacion == "Electrónico":
            estadistica.electronicos += registro.cantidad

        estadistica.save()


@receiver(post_save, sender=RegistroClasificacion)
def notificar_observer_clasificacion(sender, instance, created, **kwargs):
    if created:
        observer = ClasificacionObserver()
        observer.update(instance)