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


document.addEventListener('DOMContentLoaded', () => {
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
});


document.addEventListener("DOMContentLoaded", function () {
    const dropdownButton = document.getElementById("dropdownButton");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const mainContent = document.getElementById("mainContent");

    dropdownButton.addEventListener("click", function () {
        if (mainContent.classList.contains("with-overlay")) {
            mainContent.classList.remove("with-overlay");
        } else {
            mainContent.classList.add("with-overlay");
        }
    });

    document.addEventListener("click", function (event) {
        if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
            mainContent.classList.remove("with-overlay");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const dropdownButton = document.getElementById("dropdownButton");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const contactContent = document.getElementById("contactContent");

    dropdownButton.addEventListener("click", function () {
        if (contactContent.classList.contains("with-overlay")) {
            contactContent.classList.remove("with-overlay");
        } else {
            contactContent.classList.add("with-overlay");
        }
    });

    document.addEventListener("click", function (event) {
        if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
            contactContent.classList.remove("with-overlay");
        }
    });
});

document.getElementById("togglePassword").addEventListener("click", function () {
    const passwordInput = document.getElementById("contraseña");
    const eyeIconOpen = document.getElementById("eyeIconOpen");
    const eyeIconClosed = document.getElementById("eyeIconClosed");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIconOpen.classList.add("hidden");
        eyeIconClosed.classList.remove("hidden");
    } else {
        passwordInput.type = "password";
        eyeIconOpen.classList.remove("hidden");
        eyeIconClosed.classList.add("hidden");
    }
});

