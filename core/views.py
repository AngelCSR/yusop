from django.shortcuts import render, redirect, get_object_or_404
from .models import Tienda, Producto, ImagenProducto, Pedido, DetallePedido, Carrito, CarritoProducto
from .forms import ProductoForm, TiendaForm, ValoracionForm, PerfilForm, RegistroForm, LoginForm, CheckoutForm
from django.db.models import Q, Avg
from .carrito import Carrito as CarritoSesion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from django.core.mail import send_mail

# ==========================================
# === VISTAS PÚBLICAS (Cliente) ===
# ==========================================

def home(request):
    queryset = Producto.objects.filter(
        estado_producto='disponible',
        stock_producto__gt=0,
        tienda__estado_tienda__in=['abierta', 'pausada']
    )
    
    if request.user.is_authenticated:
        queryset = queryset.exclude(tienda__usuario=request.user)
        
    productos_destacados = queryset.order_by('-id')[:4] 
    return render(request, 'index.html', {'productos': productos_destacados})

def tiendas(request):
    query = request.GET.get('q', '')
    tiendas = Tienda.objects.all()
    
    if query:
        tiendas = tiendas.filter(
            Q(nombre_tienda__icontains=query) | 
            Q(descripcion_tienda__icontains=query)
        )
        
    return render(request, 'tiendas.html', {
        'tiendas': tiendas, 
        'query': query
    })

def productos(request):
    queryset = Producto.objects.filter(
        estado_producto='disponible', 
        stock_producto__gt=0,
        tienda__estado_tienda__in=['abierta', 'pausada']
    )
    
    if request.user.is_authenticated:
        queryset = queryset.exclude(tienda__usuario=request.user)
    
    queryset = queryset.annotate(media_estrellas=Avg('valoraciones__puntuacion'))

    query = request.GET.get('q', '')
    if query:
        queryset = queryset.filter(
            Q(nombre_producto__icontains=query) | 
            Q(tienda__nombre_tienda__icontains=query)
        )

    min_precio = request.GET.get('min_precio', '')
    max_precio = request.GET.get('max_precio', '')
    if min_precio:
        queryset = queryset.filter(precio_producto__gte=min_precio)
    if max_precio:
        queryset = queryset.filter(precio_producto__lte=max_precio)

    estrellas = request.GET.get('estrellas', '')
    if estrellas:
        queryset = queryset.filter(media_estrellas__gte=estrellas)

    en_stock = request.GET.get('en_stock', '')
    if en_stock:
        queryset = queryset.filter(stock_producto__gt=0)

    contexto = {
        'productos': queryset,
        'query': query,
        'min_precio': min_precio,
        'max_precio': max_precio,
        'estrellas': estrellas,
        'en_stock': en_stock,
    }
    
    if request.GET.get('ajax') == '1':
        return render(request, 'parcial_productos.html', contexto)

    return render(request, 'productos.html', contexto)

# --- FUNCIONES DEL CARRITO ---

def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if request.user.is_authenticated and producto.tienda.usuario == request.user:
        messages.error(request, "¡No puedes comprar tus propios productos!")
        return redirect(request.META.get('HTTP_REFERER', 'productos'))

    if request.user.is_authenticated:
        carrito_db, _ = Carrito.objects.get_or_create(id_usuario=request.user)
        item, created = CarritoProducto.objects.get_or_create(
            id_carrito=carrito_db,
            id_producto=producto,
            defaults={'cantidad_producto': cantidad}
        )
        if not created:
            item.cantidad_producto += cantidad
            item.save()
    else:
        carrito_sesion = CarritoSesion(request)
        carrito_sesion.agregar(producto, cantidad)

    messages.success(request, f'¡Añadido al carrito: {producto.nombre_producto}!')
    return redirect(request.META.get('HTTP_REFERER', 'productos'))

def ver_carrito(request):
    total = 0
    items_vista = []

    if request.user.is_authenticated:
        carrito_db = Carrito.objects.filter(id_usuario=request.user).first()
        if carrito_db:
            items_db = CarritoProducto.objects.filter(id_carrito=carrito_db).select_related('id_producto')
            for item in items_db:
                subtotal = item.id_producto.precio_producto * item.cantidad_producto
                total += subtotal
                items_vista.append({
                    'producto_id': item.id_producto.id,
                    'nombre': item.id_producto.nombre_producto,
                    'precio': item.id_producto.precio_producto,
                    'cantidad': item.cantidad_producto,
                    'acumulado': subtotal,
                    'tienda': item.id_producto.tienda.nombre_tienda
                })
    else:
        carrito_sesion = CarritoSesion(request)
        total = carrito_sesion.obtener_total()
        items_vista = carrito_sesion.carrito.values()

    return render(request, 'carrito.html', {'items': items_vista, 'total_carrito': total})

def eliminar_carrito(request, producto_id):
    if request.user.is_authenticated:
        carrito_db = Carrito.objects.filter(id_usuario=request.user).first()
        if carrito_db:
            CarritoProducto.objects.filter(id_carrito=carrito_db, id_producto_id=producto_id).delete()
    else:
        carrito_sesion = CarritoSesion(request)
        producto = get_object_or_404(Producto, id=producto_id)
        carrito_sesion.eliminar(producto)
        
    return redirect('carrito')

def restar_carrito(request, producto_id):
    if request.user.is_authenticated:
        carrito_db = Carrito.objects.filter(id_usuario=request.user).first()
        if carrito_db:
            item = CarritoProducto.objects.filter(id_carrito=carrito_db, id_producto_id=producto_id).first()
            if item:
                if item.cantidad_producto > 1:
                    item.cantidad_producto -= 1
                    item.save()
                else:
                    item.delete()
    else:
        carrito_sesion = CarritoSesion(request)
        producto = get_object_or_404(Producto, id=producto_id)
        carrito_sesion.restar(producto)
        
    return redirect('carrito')

def limpiar_carrito(request):
    if request.user.is_authenticated:
        carrito_db = Carrito.objects.filter(id_usuario=request.user).first()
        if carrito_db:
            CarritoProducto.objects.filter(id_carrito=carrito_db).delete()
    else:
        carrito_sesion = CarritoSesion(request)
        carrito_sesion.limpiar()
        
    return redirect('carrito')


# ==========================================
# === VISTAS DE AUTENTICACIÓN ===
# ==========================================

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get('username')
            contrasena = form.cleaned_data.get('password')
            user = authenticate(username=usuario, password=contrasena)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido de nuevo, {usuario}!")
                return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
        
    return render(request, 'auth/login.html', {'form': form})

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Cuenta creada con éxito! Bienvenido a yusop.")
            return redirect('home')
        else:
            messages.error(request, "Error al crear la cuenta. Revisa los datos.")
    else:
        form = RegistroForm()
        
    return render(request, 'auth/registro.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "¡Has cerrado sesión correctamente. Hasta pronto!")
    return redirect('home')



# ==========================================
# === VISTAS DEL PANEL DE CONTROL (Admin/Tienda) ===
# ==========================================

def gestion_productos(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_producto = form.save()
            
            imagen = form.cleaned_data.get('imagen_principal')
            if imagen:
                ImagenProducto.objects.create(producto=nuevo_producto, imagen=imagen)
                
            return redirect('mis_productos')
    
    else:
        form = ProductoForm()

    lista_productos = Producto.objects.all()
    
    contexto = {
        'productos': lista_productos,
        'form': form
    }
    
    return render(request, 'admin/misProductos.html', contexto)

def lista_tiendas(request):
    tus_tiendas = Tienda.objects.filter(usuario=request.user).exclude(estado_tienda='cerrada')
    return render(request, 'admin/misTiendas.html', {'tiendas': tus_tiendas})

def crear_tienda(request):
    if request.method == 'POST':
        form = TiendaForm(request.POST, request.FILES)
        if form.is_valid():
            nueva_tienda = form.save(commit=False)
            nueva_tienda.usuario = request.user
            nueva_tienda.save()
            return redirect('mis_tiendas')
    else:
        form = TiendaForm()
        
    return render(request, 'admin/crearTienda.html', {'form': form})

def editar_tienda(request, tienda_id):
    tienda = get_object_or_404(Tienda, id=tienda_id, usuario=request.user)
    
    if request.method == 'POST':
        form = TiendaForm(request.POST, request.FILES, instance=tienda)
        if form.is_valid():
            form.save()
            return redirect('mis_tiendas')
    else:
        form = TiendaForm(instance=tienda)
        
    return render(request, 'admin/crearTienda.html', {'form': form, 'editando': True})

def desactivar_tienda(request, tienda_id):
    tienda = get_object_or_404(Tienda, id=tienda_id, usuario=request.user)
    tienda.estado_tienda = 'cerrada'
    tienda.save()
    
    return redirect('mis_tiendas')

def productos_tienda(request, tienda_id):
    tienda_actual = get_object_or_404(Tienda, id=tienda_id, usuario=request.user)
    
    lista_productos = Producto.objects.filter(tienda=tienda_actual).exclude(estado_producto='retirado')
    
    contexto = {
        'tienda': tienda_actual,
        'productos': lista_productos
    }
    return render(request, 'admin/misProductos.html', contexto)


def crear_producto(request, tienda_id):
    tienda_actual = get_object_or_404(Tienda, id=tienda_id, usuario=request.user)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto_nuevo = form.save(commit=False)
            producto_nuevo.tienda = tienda_actual
            producto_nuevo.save()
            
            imagen = form.cleaned_data.get('imagen_principal')
            if imagen:
                ImagenProducto.objects.create(producto=producto_nuevo, imagen_producto=imagen)
                
            return redirect('productos_tienda', tienda_id=tienda_actual.id)
    else:
        form = ProductoForm()
        
    return render(request, 'admin/crearProducto.html', {'form': form, 'tienda': tienda_actual})


def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, tienda__usuario=request.user)
    tienda_actual = producto.tienda
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto_editado = form.save()
            
            imagen = form.cleaned_data.get('imagen_principal')
            if imagen:
                producto_editado.imagenes.all().delete()
                ImagenProducto.objects.create(producto=producto_editado, imagen_producto=imagen)
                
            return redirect('productos_tienda', tienda_id=tienda_actual.id)
    else:
        form = ProductoForm(instance=producto)
        
    return render(request, 'admin/crearProducto.html', {
        'form': form, 
        'editando': True, 
        'tienda': tienda_actual
    })

def desactivar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, tienda__usuario=request.user)
    tienda_id = producto.tienda.id
    
    producto.estado_producto = 'retirado'
    producto.save()
    
    return redirect('productos_tienda', tienda_id=tienda_id)

def detalle_tienda(request, tienda_id):
    tienda = get_object_or_404(Tienda, id=tienda_id, estado_tienda__in=['abierta', 'pausada'])
    
    productos = Producto.objects.filter(tienda=tienda, estado_producto='disponible')
    
    return render(request, 'tienda_detalle.html', {
        'tienda': tienda,
        'productos': productos
    })

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, estado_producto='disponible')
    
    valoraciones = producto.valoraciones.all().order_by('-fecha_valoracion')
    
    num_valoraciones = valoraciones.count()
    if num_valoraciones > 0:
        suma_estrellas = sum(v.puntuacion for v in valoraciones)
        media_estrellas = round(suma_estrellas / num_valoraciones, 1)
    else:
        media_estrellas = "Sin valoraciones"

    form = ValoracionForm()
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ValoracionForm()
    if request.method == 'POST':
        if request.user.is_authenticated:
            if producto.tienda.usuario == request.user:
                messages.error(request, "No puedes dejar valoraciones en tus propios productos.")
                return redirect('detalle_producto', producto_id=producto.id)

            form = ValoracionForm(request.POST)
            if form.is_valid():
                nueva_valoracion = form.save(commit=False)
                nueva_valoracion.producto = producto
                nueva_valoracion.usuario = request.user
                try:
                    nueva_valoracion.save()
                    messages.success(request, "¡Gracias por tu valoración!")
                except:
                    messages.error(request, "Hubo un error o ya has valorado este producto.")
                return redirect('detalle_producto', producto_id=producto.id)
        else:
            return redirect('login')

    contexto = {
        'producto': producto,
        'valoraciones': valoraciones,
        'media_estrellas': media_estrellas,
        'num_valoraciones': num_valoraciones,
        'form': form
    }
    return render(request, 'producto_detalle.html', contexto)

@login_required
def comprar(request):
    carrito_db = Carrito.objects.filter(id_usuario=request.user).first()
    if not carrito_db:
        return redirect('carrito')

    items = CarritoProducto.objects.filter(id_carrito=carrito_db).select_related('id_producto')
    if not items.exists():
        return redirect('carrito')

    total = sum(i.id_producto.precio_producto * i.cantidad_producto for i in items)

    pedido = Pedido.objects.create(
        fecha_pedido=timezone.now(),
        importe_pedido=total,
        id_usuario=request.user,
        estado_pedido='pendiente'
    )

    for i in items:
        producto = i.id_producto
        if producto.stock_producto < i.cantidad_producto:
            messages.error(request, f"No hay suficiente stock de {producto.nombre_producto}")
            continue

        DetallePedido.objects.create(
            cantidad_producto=i.cantidad_producto,
            precio_unitario_producto=producto.precio_producto,
            subtotal_producto=producto.precio_producto * i.cantidad_producto,
            id_producto=producto,
            id_pedido=pedido
        )

        producto.stock_producto -= i.cantidad_producto
        producto.save()

    items.delete()
    messages.success(request, "¡Pedido realizado con éxito! Gracias por tu compra.")
    return redirect('perfil')


@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Tu perfil se ha actualizado correctamente!")
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)
        
    return render(request, 'perfil.html', {
        'form': form
    })

@login_required
def mis_pedidos(request):
    usuario = request.user
    tienda = Tienda.objects.filter(usuario=usuario).first()
    
    pedidos_recibidos = []
    if tienda:
        pedidos_recibidos = DetallePedido.objects.filter(id_producto__tienda=tienda).select_related(
            'id_producto', 'id_pedido', 'id_pedido__id_usuario'
        )

    mis_compras = Pedido.objects.filter(id_usuario=usuario).order_by('-fecha_pedido')

    return render(request, 'mis_pedidos.html', {
        'pedidos_recibidos': pedidos_recibidos,
        'mis_compras': mis_compras,
        'tienda': tienda
    })

@login_required
def cambiar_estado_pedido(request, id_pedido, estado):
    pedido = get_object_or_404(Pedido, id=id_pedido)
    
    if not DetallePedido.objects.filter(id_pedido=pedido, id_producto__tienda__usuario=request.user).exists():
        # CORRECCIÓN 2: Si alguien intenta hacer trampa, lo devolvemos a 'mis_pedidos'
        return redirect('mis_pedidos')

    if estado in ['pendiente', 'enviado', 'completado']:
        pedido.estado_pedido = estado
        pedido.save()
        messages.success(request, f"El estado del pedido #{pedido.id} se ha actualizado a '{estado}'.")

    return redirect('mis_pedidos')

@login_required
def checkout(request):
    total = 0
    carrito_db = Carrito.objects.filter(id_usuario=request.user).first()
    
    if not carrito_db:
        return redirect('carrito')
        
    items_carrito = CarritoProducto.objects.filter(id_carrito=carrito_db).select_related('id_producto')
    
    if not items_carrito.exists():
        return redirect('carrito')
        
    total = sum(item.id_producto.precio_producto * item.cantidad_producto for item in items_carrito)
        
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = Pedido.objects.create(
                fecha_pedido=timezone.now(),
                importe_pedido=total,
                id_usuario=request.user,
                estado_pedido='pendiente'
            )

            texto_articulos = ""

            for i in items_carrito:
                producto = i.id_producto
                if producto.stock_producto < i.cantidad_producto:
                    messages.error(request, f"No hay suficiente stock de {producto.nombre_producto}")
                    continue

                DetallePedido.objects.create(
                    cantidad_producto=i.cantidad_producto,
                    precio_unitario_producto=producto.precio_producto,
                    subtotal_producto=producto.precio_producto * i.cantidad_producto,
                    id_producto=producto,
                    id_pedido=pedido
                )

                texto_articulos += f"- {i.cantidad_producto}x {producto.nombre_producto} ({producto.precio_producto}€/ud)\n"

                producto.stock_producto -= i.cantidad_producto
                producto.save()

            email_comprador = form.cleaned_data.get('email')
            nombre_comprador = form.cleaned_data.get('nombre_completo')
            
            asunto = f"Confirmación de tu pedido #{pedido.id} en Yusop"
            mensaje = f"""Hola {nombre_comprador},

¡Gracias por tu compra en Yusop! Hemos recibido tu pedido y se está procesando.

Resumen de tu pedido:
{texto_articulos}
-------------------------------------
Total pagado: {total:.2f}€
Método de pago: {form.cleaned_data.get('metodo_pago').upper()}

Puedes hacer seguimiento del envío desde el panel de 'Mis Pedidos' en tu perfil.

Un saludo,
El equipo de Yusop."""

            send_mail(asunto, mensaje, 'info@yusop.com', [email_comprador], fail_silently=True)

            items_carrito.delete()
            messages.success(request, "¡Pedido realizado con éxito! Te hemos enviado un email con los detalles.")
            return redirect('mis_pedidos')
    else:
        datos_iniciales = {
            'nombre_completo': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=datos_iniciales)
        
    contexto = {
        'form': form,
        'total': total
    }
        
    return render(request, 'tienda/checkout.html', contexto)

def buscador_global(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('productos')
        
    hay_tiendas = Tienda.objects.filter(
        Q(nombre_tienda__icontains=query) | 
        Q(descripcion_tienda__icontains=query)
    ).exists()
    
    hay_productos = Producto.objects.filter(
        Q(nombre_producto__icontains=query) | 
        Q(descripcion_producto__icontains=query)
    ).exists()
    
    if hay_tiendas and not hay_productos:
        return redirect(f"{reverse('tiendas')}?q={query}")
    else:
        return redirect(f"{reverse('productos')}?q={query}")