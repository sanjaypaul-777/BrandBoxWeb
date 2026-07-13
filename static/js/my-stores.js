/**
 * My Stores — search, status filters, ⋯ menu, disconnect confirm.
 */
(function () {
  var root = document.querySelector("[data-my-stores]");
  if (!root) return;

  var search = root.querySelector("[data-ms-search]");
  var list = root.querySelector("[data-ms-list]");
  var emptyFilter = root.querySelector("[data-ms-empty-filter]");
  var pills = root.querySelectorAll("[data-ms-filter]");
  var confirm = root.querySelector("[data-ms-confirm]");
  var confirmShop = root.querySelector("[data-ms-confirm-shop]");
  var confirmForm = root.querySelector("[data-ms-confirm-form]");
  var activeFilter = "all";

  function applyFilters() {
    if (!list) return;
    var q = ((search && search.value) || "").trim().toLowerCase();
    var visible = 0;
    list.querySelectorAll("[data-ms-row]").forEach(function (row) {
      var status = row.getAttribute("data-status") || "";
      var shop = row.getAttribute("data-shop") || "";
      var statusOk = activeFilter === "all" || status === activeFilter;
      var searchOk = !q || shop.indexOf(q) !== -1;
      var show = statusOk && searchOk;
      row.hidden = !show;
      if (show) visible += 1;
    });
    if (emptyFilter) emptyFilter.hidden = visible > 0;
  }

  if (search) {
    search.addEventListener("input", applyFilters);
  }

  pills.forEach(function (pill) {
    pill.addEventListener("click", function () {
      activeFilter = pill.getAttribute("data-ms-filter") || "all";
      pills.forEach(function (p) {
        var on = p === pill;
        p.classList.toggle("is-active", on);
        p.setAttribute("aria-pressed", on ? "true" : "false");
      });
      applyFilters();
    });
  });

  function closeMenus(except) {
    root.querySelectorAll("[data-ms-menu].is-open").forEach(function (menu) {
      if (menu === except) return;
      menu.classList.remove("is-open");
      var panel = menu.querySelector(".ms-menu__panel");
      var btn = menu.querySelector("[data-ms-menu-btn]");
      if (panel) panel.hidden = true;
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  }

  root.addEventListener("click", function (e) {
    var menuBtn = e.target.closest("[data-ms-menu-btn]");
    if (menuBtn) {
      e.preventDefault();
      var menu = menuBtn.closest("[data-ms-menu]");
      var open = menu.classList.contains("is-open");
      closeMenus();
      if (!open) {
        menu.classList.add("is-open");
        var panel = menu.querySelector(".ms-menu__panel");
        if (panel) panel.hidden = false;
        menuBtn.setAttribute("aria-expanded", "true");
      }
      return;
    }

    var disconnect = e.target.closest("[data-ms-disconnect]");
    if (disconnect && confirm && confirmForm) {
      e.preventDefault();
      closeMenus();
      confirmShop.textContent = disconnect.getAttribute("data-shop") || "this store";
      confirmForm.action = disconnect.getAttribute("data-action") || "";
      confirm.hidden = false;
      document.body.style.overflow = "hidden";
      return;
    }

    if (!e.target.closest("[data-ms-menu]")) closeMenus();
  });

  function closeConfirm() {
    if (!confirm) return;
    confirm.hidden = true;
    document.body.style.overflow = "";
  }

  root.querySelectorAll("[data-ms-confirm-cancel]").forEach(function (btn) {
    btn.addEventListener("click", closeConfirm);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeMenus();
      closeConfirm();
    }
  });
})();
