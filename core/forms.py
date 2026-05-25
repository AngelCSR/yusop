from django import forms
from .models import Producto, Tienda, Valoracion
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class ProductoForm(forms.ModelForm):
    imagen_principal = forms.ImageField(
        required=False, 
        label="Imagen del Producto",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion_producto', 'precio_producto', 'stock_producto', 'estado_producto']
        
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Reloj Casio'}),
            'descripcion_producto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_producto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_producto': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado_producto': forms.Select(attrs={'class': 'form-select'}),
        }

class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = ['nombre_tienda', 'descripcion_tienda', 'avatar_tienda', 'banner_tienda'] 
        
        widgets = {
            'nombre_tienda': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_tienda': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar_tienda': forms.FileInput(attrs={'class': 'form-control'}),
            # Añade este widget para el banner:
            'banner_tienda': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ValoracionForm(forms.ModelForm):
    class Meta:
        model = Valoracion
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.Select(attrs={'class': 'form-select'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '¿Qué te ha parecido este producto? Cuéntanos tu experiencia...'}),
        }

Usuario = get_user_model()

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'avatar_usuario']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu email'}),
            'avatar_usuario': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'avatar_usuario': 'Foto de perfil'
        }

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus apellidos'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}))

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CheckoutForm(forms.Form):
    METODOS_PAGO = [
        ('tarjeta', 'Tarjeta de Crédito / Débito'),
        ('paypal', 'PayPal'),
        ('bizum', 'Bizum'),
        ('transferencia', 'Transferencia Bancaria')
    ]
    
    nombre_completo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y apellidos'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}))
    telefono = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu número de móvil'}))
    
    direccion = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle, número, piso, puerta...'}))
    localidad = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad o pueblo'}))
    provincia = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Provincia'}))
    codigo_postal = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}))
    
    metodo_pago = forms.ChoiceField(choices=METODOS_PAGO, widget=forms.Select(attrs={'class': 'form-select'}))