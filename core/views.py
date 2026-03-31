from django.shortcuts import render
from .models import Producto

def home(request):
    productos = Producto.objects.all()[:4] 
    return render(request, 'index.html', {'productos_destacados': productos})

def tiendas(request):
    return render(request, 'tiendas.html')

def productos(request):
    return render(request, 'productos.html')

def carrito(request):
    return render(request, 'cliente/carritoSimulado.html')

def login_view(request):
    return render(request, 'auth/login.html')

def registro(request):
    return render(request, 'auth/registro.html')

def perfil(request):
    return render(request, 'auth/perfil.html')

def logout_view(request):
    # Temporalmente redirigimos al home hasta que configuremos el logout real
    return render(request, 'index.html')