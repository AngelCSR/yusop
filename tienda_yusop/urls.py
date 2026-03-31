from django.contrib import admin
from django.urls import path
from core import views # Importamos tus vistas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('tiendas/', views.tiendas, name='tiendas'),
    path('productos/', views.productos, name='productos'),
    path('carrito/', views.carrito, name='carrito'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', views.logout_view, name='logout'),
]