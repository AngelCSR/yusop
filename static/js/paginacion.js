function paginar({
    contenedorId,
    paginationId,
    itemsPorPagina = 8,
    itemSelector = ":scope > div"
}) {

    const contenedor = document.getElementById(contenedorId);
    const pagination = document.getElementById(paginationId);

    if (!contenedor || !pagination) return;

    let paginaActual = 1;

    function getItems() {
        return Array.from(contenedor.querySelectorAll(itemSelector));
    }

    function render() {

        const items = getItems();

        const inicio = (paginaActual - 1) * itemsPorPagina;
        const fin = inicio + itemsPorPagina;

        items.forEach((item, i) => {
            item.style.display = (i >= inicio && i < fin) ? "" : "none";
        });

        renderBotones(items.length);
    }

    function renderBotones(totalItems) {

        const total = Math.max(1, Math.ceil(totalItems / itemsPorPagina));

        pagination.innerHTML = "";

        // ANTERIOR
        const prev = document.createElement("li");
        prev.className = `page-item ${paginaActual === 1 ? "disabled" : ""}`;
        prev.innerHTML = `<a class="page-link" href="#">Anterior</a>`;
        prev.onclick = (e) => {
            e.preventDefault();
            if (paginaActual > 1) {
                paginaActual--;
                render();
            }
        };
        pagination.appendChild(prev);

        // NÚMEROS
        for (let i = 1; i <= total; i++) {

            const li = document.createElement("li");
            li.className = `page-item ${i === paginaActual ? "active" : ""}`;
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;

            li.onclick = (e) => {
                e.preventDefault();
                paginaActual = i;
                render();
            };

            pagination.appendChild(li);
        }

        // SIGUIENTE
        const next = document.createElement("li");
        next.className = `page-item ${paginaActual === total ? "disabled" : ""}`;
        next.innerHTML = `<a class="page-link" href="#">Siguiente</a>`;
        next.onclick = (e) => {
            e.preventDefault();
            if (paginaActual < total) {
                paginaActual++;
                render();
            }
        };

        pagination.appendChild(next);
    }

    render();
}


// ============================
// INICIALIZACIÓN GLOBAL
// ============================

document.addEventListener("DOMContentLoaded", () => {

    // PRODUCTOS (cards)
    paginar({
        contenedorId: "contenedorProductos",
        paginationId: "pagination",
        itemsPorPagina: 8
    });

    // TIENDAS
    paginar({
        contenedorId: "listaTiendas",
        paginationId: "paginationTiendas",
        itemsPorPagina: 6
    });

    // CATÁLOGO TIENDA
    paginar({
        contenedorId: "contenedorCatalogo",
        paginationId: "paginationCatalogo",
        itemsPorPagina: 8,
        itemSelector: ".producto-catalogo"
    });

    // ADMIN PRODUCTOS (TABLA)
    paginar({
        contenedorId: "contenedorProductosAdmin",
        paginationId: "paginationAdmin",
        itemsPorPagina: 8,
        itemSelector: "tr"
    });

});