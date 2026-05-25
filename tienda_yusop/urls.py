from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('tiendas/', views.tiendas, name='tiendas'),
    path('productos/', views.productos, name='productos'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', views.logout_view, name='logout'),
    path('comprar/', views.comprar, name='comprar'),
    path('panel/mis-productos/', views.gestion_productos, name='mis_productos'),
    path('panel/mis-tiendas/', views.lista_tiendas, name='mis_tiendas'),
    path('panel/mis-tiendas/nueva/', views.crear_tienda, name='crear_tienda'),
    path('panel/mis-tiendas/editar/<int:tienda_id>/', views.editar_tienda, name='editar_tienda'),
    path('panel/mis-tiendas/desactivar/<int:tienda_id>/', views.desactivar_tienda, name='desactivar_tienda'),
    path('panel/mis-tiendas/<int:tienda_id>/productos/', views.productos_tienda, name='productos_tienda'),
    path('panel/productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('panel/productos/desactivar/<int:producto_id>/', views.desactivar_producto, name='desactivar_producto'),
    path('panel/mis-tiendas/<int:tienda_id>/productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('tiendas/<int:tienda_id>/', views.detalle_tienda, name='detalle_tienda'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/restar/<int:producto_id>/', views.restar_carrito, name='restar_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito/limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('tienda/<int:tienda_id>/', views.detalle_tienda, name='ver_tienda'),
    path('pedido/<int:id_pedido>/estado/<str:estado>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('checkout/', views.checkout, name='checkout'),
    path('buscar/', views.buscador_global, name='buscador_global'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)