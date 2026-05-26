from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Usuario(AbstractUser):
    telefono_usuario = models.CharField(max_length=20, null=True, blank=True)
    tarjeta_usuario = models.BigIntegerField(null=True, blank=True)
    avatar_usuario = models.ImageField(upload_to='usuarios/avatars/', null=True, blank=True)

    @property
    def avatar_url(self):
        if self.avatar_usuario and self.avatar_usuario.url:
            return self.avatar_usuario.url
        return settings.STATIC_URL + 'img/usuario_con_fondo_gris.png'
    
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
    nombre_tienda = models.CharField(max_length=100, unique=True)
    descripcion_tienda = models.TextField(null=True, blank=True)
    avatar_tienda = models.ImageField(upload_to='tiendas/avatars/', null=True, blank=True)
    banner_tienda = models.ImageField(upload_to='tiendas/banners/', null=True, blank=True)

    @property
    def avatar_url(self):
        if self.avatar_tienda and self.avatar_tienda.url:
            return self.avatar_tienda.url
        return settings.STATIC_URL + 'img/tienda.png'

    @property
    def banner_url(self):
        if self.banner_tienda and self.banner_tienda.url:
            return self.banner_tienda.url
        return settings.STATIC_URL + 'img/banner.png'
    
    ESTADO_TIENDA = [
        ('abierta', 'Abierta'),
        ('pausada', 'Pausada'),
        ('cerrada', 'Cerrada'),
    ]
    estado_tienda = models.CharField(max_length=15, choices=ESTADO_TIENDA, default='abierta')
    
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='mis_tiendas')

    def __str__(self):
        return self.nombre_tienda


class Producto(models.Model):
    nombre_producto = models.CharField(max_length=100)
    descripcion_producto = models.TextField(null=True, blank=True)
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2)
    stock_producto = models.IntegerField(default=0)
    imagen_principal = models.ImageField(upload_to='productos/', null=True, blank=True)

    @property
    def image_url(self):
        if self.imagen_principal and self.imagen_principal.url:
            return self.imagen_principal.url
        return settings.STATIC_URL + 'img/item.png'
    
    ESTADO_PRODUCTO = [
        ('disponible', 'Disponible'),
        ('pausado', 'Pausado'),
        ('retirado', 'Retirado'),
    ]
    estado_producto = models.CharField(max_length=15, choices=ESTADO_PRODUCTO, default='disponible')
    
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')

    def __str__(self):
        return self.nombre_producto


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen_producto = models.ImageField(upload_to='productos/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre_producto}"
    

class DireccionUsuario(models.Model):
    direccion_usuario = models.CharField(max_length=255)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='direcciones')

    class Meta:
        unique_together = ('direccion_usuario', 'usuario')


class DireccionTienda(models.Model):
    direccion_tienda = models.CharField(max_length=255) # Renombrado
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='direcciones')

    class Meta:
        unique_together = ('direccion_tienda', 'tienda')


class Valoracion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='valoraciones')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='valoraciones')
    
    puntuacion = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['producto', 'usuario'], name='unique_valoracion_usuario')
        ]

    def __str__(self):
        return f"{self.puntuacion}★ por {self.usuario.username} para {self.producto.nombre_producto}"

class Carrito(models.Model):
    id_carrito = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('core.Usuario', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carrito'


class CarritoProducto(models.Model):
    id_carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_producto = models.IntegerField(default=1)

    class Meta:
        db_table = 'carrito_productos'
        unique_together = ('id_carrito', 'id_producto')

class Pedido(models.Model):
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    importe_pedido = models.DecimalField(max_digits=12, decimal_places=2)
    id_usuario = models.ForeignKey('core.Usuario', on_delete=models.CASCADE)
    estado_pedido = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('enviado', 'Enviado'),
            ('completado', 'Completado')
        ],
        default='pendiente'
    )

    class Meta:
        db_table = 'core_pedido' 


class DetallePedido(models.Model):
    cantidad_producto = models.IntegerField()
    precio_unitario_producto = models.DecimalField(max_digits=7, decimal_places=2)
    subtotal_producto = models.DecimalField(max_digits=12, decimal_places=2)
    
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles')
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')

    class Meta:
        db_table = 'core_detallepedido'