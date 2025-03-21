document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("dark-mode-toggle");
    const body = document.body;
    const sunIcon = document.getElementById("sun-icon");
    const moonIcon = document.getElementById("moon-icon");
    const logo = document.querySelector(".logo-login"); // Seleccionar el logo

    // Verifica si hay un tema guardado en localStorage
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        sunIcon.style.display = "block";
        moonIcon.style.display = "none";
        logo.style.filter = "invert(1)"; // Hace el logo blanco
    } else {
        body.classList.add("light-mode");
        sunIcon.style.display = "none";
        moonIcon.style.display = "block";
        moonIcon.style.fill = "black";
        logo.style.filter = "invert(0)"; // Mantiene el logo negro
    }

    toggleButton.addEventListener("click", function () {
        body.classList.toggle("dark-mode");
        body.classList.toggle("light-mode");

        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
            sunIcon.style.display = "block";
            moonIcon.style.display = "none";
            logo.style.filter = "invert(1)"; // Logo blanco en modo oscuro
        } else {
            localStorage.setItem("theme", "light");
            sunIcon.style.display = "none";
            moonIcon.style.display = "block";
            moonIcon.style.fill = "black";
            logo.style.filter = "invert(0)"; // Logo negro en modo claro
        }
    });
});

