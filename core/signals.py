from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Carrito, CarritoProducto, Producto

@receiver(user_logged_in)
def trasladar_carrito_sesion_a_base_datos(sender, request, user, **kwargs):
    carrito_sesion = request.session.get('carrito', {})
    
    if carrito_sesion:
        carrito_db, _ = Carrito.objects.get_or_create(id_usuario=user)
        
        for producto_id, datos in carrito_sesion.items():
            producto = Producto.objects.get(id=producto_id)
            
            item, created = CarritoProducto.objects.get_or_create(
                id_carrito=carrito_db,
                id_producto=producto,
                defaults={'cantidad_producto': datos['cantidad']}
            )
            
            if not created:
                item.cantidad_producto += datos['cantidad']
                item.save()
        
        request.session['carrito'] = {}
        request.session.modified = True