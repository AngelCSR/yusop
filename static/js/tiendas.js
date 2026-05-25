document.addEventListener('DOMContentLoaded', function() {
    const buscador = document.getElementById('buscadorTiendas');
    
    if (buscador) {
        buscador.addEventListener('input', function() {
            const filtro = this.value.toLowerCase();
            
            document.querySelectorAll('.card-tienda-wrapper').forEach(wrapper => {
                const card = wrapper.querySelector('.card-tienda');
                const nombre = card.dataset.nombre || '';
                const descripcion = card.dataset.descripcion || '';
                
                if (nombre.includes(filtro) || descripcion.includes(filtro)) {
                    wrapper.style.display = '';
                } else {
                    wrapper.style.display = 'none';
                }
            });
        });
    }
});