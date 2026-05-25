document.addEventListener("DOMContentLoaded", function() {
    
    const formFiltros = document.getElementById('formFiltros');
    const contenedor = document.getElementById('contenedorProductos');

    if (formFiltros && contenedor) {
        formFiltros.addEventListener('input', function(e) {
            
            const formData = new FormData(formFiltros);
            const params = new URLSearchParams(formData);
            
            params.append('ajax', '1');
            
            const url = `${formFiltros.action}?${params.toString()}`;

            fetch(url)
                .then(response => response.text())
                .then(html => {
                    contenedor.innerHTML = html;
                })
                .catch(error => console.error('Error al filtrar:', error));
        });
    }
});