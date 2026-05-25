from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Carrito

class Command(BaseCommand):
    help = 'Borra de la base de datos los carritos abandonados hace más de 30 días'

    def handle(self, *args, **options) :
        # Calculamos la fecha límite (Hoy menos 30 días)
        fecha_limite = timezone.now() - timedelta(days=30)
        
        carritos_antiguos = Carrito.objects.filter(fecha_creacion__lt=fecha_limite)
        
        cantidad = carritos_antiguos.count()
        
        carritos_antiguos.delete()

        self.stdout.write(self.style.SUCCESS(f'Éxito: Se han eliminado {cantidad} carritos abandonados.'))