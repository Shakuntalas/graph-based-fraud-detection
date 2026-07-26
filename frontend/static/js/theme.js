const THEME_KEY = "graphFraudTheme";

export function initTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY) || "dark";
  applyTheme(savedTheme);

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextTheme = document.body.dataset.theme === "light" ? "dark" : "light";
      applyTheme(nextTheme);
      localStorage.setItem(THEME_KEY, nextTheme);
      window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: nextTheme } }));
    });
  });
}

function applyTheme(theme) {
  document.body.dataset.theme = theme;
  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.textContent = theme === "light" ? "Dark mode" : "Light mode";
    button.setAttribute("aria-label", `Switch to ${theme === "light" ? "dark" : "light"} mode`);
  });
}
