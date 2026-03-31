let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

function renderCarrito() {
    const tabla = document.getElementById('tablaCarrito');
    const totalSpan = document.getElementById('totalGeneral');
    
    if (!tabla) return; 

    tabla.innerHTML = '';
    let totalGeneral = 0;

    if (carrito.length === 0) {
        tabla.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">El carrito está vacío</td></tr>';
        if(totalSpan) totalSpan.textContent = '0.00';
        return;
    }

    carrito.forEach((p, i) => {
        const subtotal = p.precio * p.cantidad;
        totalGeneral += subtotal;

        tabla.innerHTML += `
            <tr>
                <td class="fw-bold">${p.nombre}</td>
                <td>${parseFloat(p.precio).toFixed(2)}€</td>
                <td>
                    <input type="number" value="${p.cantidad}" min="1" 
                           class="form-control form-control-sm" style="width:70px"
                           onchange="actualizarCantidad(${i}, this.value)">
                </td>
                <td class="fw-bold text-success">${subtotal.toFixed(2)}€</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminar(${i})">
                        Eliminar
                    </button>
                </td>
            </tr>
        `;
    });

    if(totalSpan) totalSpan.textContent = totalGeneral.toFixed(2);
    guardarCarrito();
}

function actualizarCantidad(i, cantidad) {
    carrito[i].cantidad = parseInt(cantidad);
    renderCarrito();
}

function eliminar(i) {
    carrito.splice(i, 1);
    renderCarrito();
}

function vaciarCarrito() {
    if(confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
        carrito = [];
        renderCarrito();
    }
}

function guardarCarrito() {
    localStorage.setItem('carrito', JSON.stringify(carrito));
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', renderCarrito);