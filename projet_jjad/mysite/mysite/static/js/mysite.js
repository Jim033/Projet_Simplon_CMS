// Menu burger : sans JavaScript, le bouton reste caché et le menu reste visible
const menuBouton = document.querySelector(".menu-bouton");

if (menuBouton) {
    const header = menuBouton.closest("header");

    const basculerMenu = (ouvert) => {
        menuBouton.setAttribute("aria-expanded", ouvert);
        header.classList.toggle("menu-replie", !ouvert);
    };

    menuBouton.hidden = false;
    basculerMenu(false);

    menuBouton.addEventListener("click", () => {
        basculerMenu(menuBouton.getAttribute("aria-expanded") !== "true");
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && menuBouton.getAttribute("aria-expanded") === "true") {
            basculerMenu(false);
            menuBouton.focus();
        }
    });
}
