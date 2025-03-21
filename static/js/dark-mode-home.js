document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("dark-mode-toggle-home");
    const body = document.body;
    const mainContent = document.getElementById("mainContent");
    const sunIcon = document.getElementById("sun-icon-home");
    const moonIcon = document.getElementById("moon-icon-home");
    const cardOne = document.getElementById("card-one");
    const h2 = document.getElementById("h2"); // Referencia a h2
    const p1 = document.getElementById("p1"); // Referencia a p1

    // Función para agregar clases a cada li dentro de #card-one
    function addCardStyles() {
        if (cardOne) {
            cardOne.querySelectorAll("li").forEach(li => {
                li.classList.add("rounded-lg", "bg-white");
            });
        }
    }

    // Función para remover las clases de cada li dentro de #card-one
    function removeCardStyles() {
        if (cardOne) {
            cardOne.querySelectorAll("li").forEach(li => {
                li.classList.remove("rounded-lg", "bg-white");
            });
        }
    }

    function applyDarkMode() {
        body.classList.add("dark", "bg-gray-900");
        mainContent.classList.add("bg-gray-900");
        localStorage.setItem("theme-home", "dark");
        sunIcon.classList.remove("hidden");
        moonIcon.classList.add("hidden");

        // Cambiar el color de h2 y p1 a blanco en modo oscuro
        if (h2) {
            h2.style.color = "white";
        }
        if (p1) {
            p1.style.color = "white";
        }

        // Agregar estilos a los li de #card-one
        addCardStyles();
    }

    function removeDarkMode() {
        body.classList.remove("dark", "bg-gray-900");
        mainContent.classList.remove("bg-gray-900");
        localStorage.setItem("theme-home", "light");
        sunIcon.classList.add("hidden");
        moonIcon.classList.remove("hidden");

        // Remover el color blanco de h2 y p1 cuando el modo oscuro se apaga
        if (h2) {
            h2.style.color = ""; // Deja el color predeterminado o el especificado en CSS
        }
        if (p1) {
            p1.style.color = ""; // Deja el color predeterminado o el especificado en CSS
        }

        // Remover estilos a los li de #card-one
        removeCardStyles();
    }

    if (localStorage.getItem("theme-home") === "dark") {
        applyDarkMode();
    } else {
        removeDarkMode();
    }

    toggleButton.addEventListener("click", function () {
        if (body.classList.contains("dark")) {
            removeDarkMode();
        } else {
            applyDarkMode();
        }
    });
});



