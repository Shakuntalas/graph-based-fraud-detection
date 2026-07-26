import { initAdminAuth } from "./auth/adminAuth.js";
import { initAuthPage } from "./auth/userAuth.js";
import { initAdminDashboard } from "./dashboard/adminDashboard.js";
import { initUserDashboardPage } from "./dashboard/userDashboard.js";
import { initMonitorPage } from "./monitor/scanner.js";
import { initTheme } from "./theme.js";

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  initTheme();

  if (page === "auth") {
    initAuthPage();
  }

  if (page === "admin") {
    initAdminDashboard();
    initAdminAuth();
  }

  if (page === "dashboard") {
    initMonitorPage();
    initUserDashboardPage();

    const logoutBtn = document.getElementById("userLogoutButton");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", async () => {
        await fetch("/api/logout", { method: "POST" });
        window.location.href = "/login";
      });
    }
  }
});
