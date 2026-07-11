(() => {
  "use strict";

  const header = document.querySelector("#site-header");
  const navbar = document.querySelector("#navbar-shell");
  const menuButton = document.querySelector("#mobile-menu-btn");
  const menu = document.querySelector("#mobile-menu");
  const menuIcon = document.querySelector("#btn_icone");
  let scrollScheduled = false;

  const updateHeader = () => {
    const scrolled = window.scrollY > 24;
    header?.classList.toggle("site-header-scrolled", scrolled);
    navbar?.classList.toggle("navbar-scrolled", scrolled);
    scrollScheduled = false;
  };

  const closeMenu = ({ restoreFocus = false } = {}) => {
    if (!menu || !menuButton || !menuIcon) return;
    menu.classList.remove("is-open");
    menu.setAttribute("aria-hidden", "true");
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Ouvrir le menu");
    menuIcon.classList.replace("fa-x", "fa-bars");
    document.body.classList.remove("mobile-menu-open");
    if (restoreFocus) menuButton.focus();
  };

  const openMenu = () => {
    if (!menu || !menuButton || !menuIcon) return;
    menu.classList.add("is-open");
    menu.setAttribute("aria-hidden", "false");
    menuButton.setAttribute("aria-expanded", "true");
    menuButton.setAttribute("aria-label", "Fermer le menu");
    menuIcon.classList.replace("fa-bars", "fa-x");
    document.body.classList.add("mobile-menu-open");
    menu.querySelector("a")?.focus();
  };

  menuButton?.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") === "true";
    isOpen ? closeMenu() : openMenu();
  });

  menu?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => closeMenu());
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuButton?.getAttribute("aria-expanded") === "true") {
      closeMenu({ restoreFocus: true });
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 1280) closeMenu();
  }, { passive: true });

  window.addEventListener("scroll", () => {
    if (!scrollScheduled) {
      window.requestAnimationFrame(updateHeader);
      scrollScheduled = true;
    }
  }, { passive: true });

  updateHeader();
})();
