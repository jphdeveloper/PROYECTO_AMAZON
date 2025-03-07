document.addEventListener("DOMContentLoaded", function () {
    const dropdownButton = document.getElementById("dropdownButton");
    const dropdownMenu = document.getElementById("dropdownMenu");

    if (!dropdownButton || !dropdownMenu) {
        console.error("No se encontraron los elementos del dropdown.");
        return;
    }

    dropdownButton.addEventListener("click", function () {
        dropdownMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", function (event) {
        if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.add("hidden");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("dropdownBtn");
    const menu = document.getElementById("dropdownMn");

    button.addEventListener("click", function (event) {
        menu.classList.toggle("hidden");
        event.stopPropagation();
    });

    document.addEventListener("click", function (event) {
        if (!button.contains(event.target) && !menu.contains(event.target)) {
            menu.classList.add("hidden");
        }
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menuToggle");
    const menuDropdown = document.getElementById("menuDropdown");

    menuToggle.addEventListener("click", function (event) {
        menuDropdown.classList.toggle("hidden");
        event.stopPropagation();
    });

    document.addEventListener("click", function (event) {
        if (!menuDropdown.contains(event.target) && !menuToggle.contains(event.target)) {
            menuDropdown.classList.add("hidden");
        }
    });
});


const botonMiCuenta = document.getElementById('mi-cuenta');
const menuFlotante = document.getElementById('menu-flotante');

botonMiCuenta.addEventListener('click', (event) => {
    event.preventDefault();
    menuFlotante.classList.toggle('hidden');
});

document.addEventListener('click', (event) => {
    if (!botonMiCuenta.contains(event.target) && !menuFlotante.contains(event.target)) {
        menuFlotante.classList.add('hidden');
    }
});
