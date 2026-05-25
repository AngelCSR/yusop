class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        
        if not carrito:
            carrito = self.session["carrito"] = {}
        
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        id_producto = str(producto.id)
        
        if id_producto not in self.carrito.keys():
            self.carrito[id_producto] = {
                "producto_id": producto.id,
                "nombre": producto.nombre_producto,
                "precio": float(producto.precio_producto),
                "cantidad": cantidad,
                "acumulado": float(producto.precio_producto) * cantidad,
                "tienda": producto.tienda.nombre_tienda
            }
        else:
            self.carrito[id_producto]["cantidad"] += cantidad
            self.carrito[id_producto]["acumulado"] += float(producto.precio_producto) * cantidad
            
        self.guardar_carrito()

    def restar(self, producto):
        id_producto = str(producto.id)
        if id_producto in self.carrito.keys():
            self.carrito[id_producto]["cantidad"] -= 1
            self.carrito[id_producto]["acumulado"] -= float(producto.precio_producto)
            
            # Si la cantidad baja a 0, lo borramos del carrito
            if self.carrito[id_producto]["cantidad"] <= 0:
                self.eliminar(producto)
            else:
                self.guardar_carrito()

    def eliminar(self, producto):
        id_producto = str(producto.id)
        if id_producto in self.carrito:
            del self.carrito[id_producto]
            self.guardar_carrito()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True
        self.session.save()
        
    def obtener_total(self):
        total = 0
        for item in self.carrito.values():
            total += float(item["acumulado"])
        return total