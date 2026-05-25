document.addEventListener('DOMContentLoaded', function() {
    const selectPago = document.querySelector('select[name="metodo_pago"]');
    const opciones = document.querySelectorAll('.pago-opcion');

    function mostrarOpcionPago() {
        opciones.forEach(el => el.style.display = 'none');
        const valor = selectPago.value;
        if (valor) {
            const elementoMostrar = document.getElementById('datos-' + valor);
            if (elementoMostrar) {
                elementoMostrar.style.display = 'block';
            }
        }
    }

    if(selectPago) {
        selectPago.addEventListener('change', mostrarOpcionPago);
        mostrarOpcionPago();
    }
});