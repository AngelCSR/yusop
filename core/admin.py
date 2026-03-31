from django.contrib import admin
from .models import Usuario, Tienda, Producto

# Registramos tus modelos para que sean visibles
admin.site.register(Usuario)
admin.site.register(Tienda)
admin.site.register(Producto)