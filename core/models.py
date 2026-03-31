from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # Campos que no trae Django
    telefono_usuario = models.IntegerField(null=True, blank=True)
    tarjeta_usuario = models.BigIntegerField(null=True, blank=True)
    avatar_usuario = models.ImageField(default='usuario.png', upload_to='avatars/')
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
    ]
    estado_usuario = models.CharField(
        max_length=10, 
        choices=ESTADO_CHOICES, 
        default='activo'
    )

    def __str__(self):
        return self.username
    
class Tienda(models.Model):
    nombre_tienda = models.CharField(max_length=30)
    descripcion_tienda = models.TextField(max_length=1000, null=True, blank=True)
    avatar_tienda = models.ImageField(default='tienda.png', upload_to='tiendas/')
    
    ESTADO_TIENDA = [
        ('abierta', 'Abierta'),
        ('pausada', 'Pausada'),
        ('cerrada', 'Cerrada'),
    ]
    estado_tienda = models.CharField(max_length=7, choices=ESTADO_TIENDA, default='abierta')
    
    # Relación con Usuario (id_usuario INT)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='mis_tiendas')

    def __str__(self):
        return self.nombre_tienda

class Producto(models.Model):
    nombre_producto = models.CharField(max_length=30)
    descripcion_producto = models.TextField(max_length=1000, null=True, blank=True)
    precio_producto = models.DecimalField(max_digits=7, decimal_places=2)
    stock_producto = models.IntegerField()
    
    ESTADO_PRODUCTO = [
        ('disponible', 'Disponible'),
        ('pausado', 'Pausado'),
        ('retirado', 'Retirado'),
    ]
    estado_producto = models.CharField(max_length=10, choices=ESTADO_PRODUCTO, default='disponible')
    
    # Relación con Tienda (id_tienda INT)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')

    def __str__(self):
        return self.nombre_producto
    
class DireccionUsuario(models.Model):
    direccion = models.CharField(max_length=100)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='direcciones')

    class Meta:
        unique_together = ('direccion', 'usuario') # Equivale a tu CONSTRAINT UNIQUE

class DireccionTienda(models.Model):
    direccion = models.CharField(max_length=100)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='direcciones')

    class Meta:
        unique_together = ('direccion', 'tienda')

class Pedido(models.Model):
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    importe_pedido = models.DecimalField(max_digits=12, decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=7, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        # Quitamos primary_key = False y dejamos solo la restricción de unicidad
        constraints = [
            models.UniqueConstraint(fields=['pedido', 'producto'], name='unique_pedido_producto')
        ]

    def __str__(self):
        return f"Detalle de {self.pedido.id} - {self.producto.nombre_producto}"