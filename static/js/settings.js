/**
 * Settings — notification toggles, default niche, delete confirm.
 */
(function () {
  var root = document.querySelector("[data-settings]");
  if (!root) return;

  var csrf =
    (document.querySelector("[name=csrfmiddlewaretoken]") &&
      document.querySelector("[name=csrfmiddlewaretoken]").value) ||
    "";
  var notifyUrl = root.getAttribute("data-notify-url") || "";
  var nicheUrl = root.getAttribute("data-niche-url") || "";
  var notifyStatus = root.querySelector("[data-notify-status]");
  var nicheStatus = root.querySelector("[data-niche-status]");

  function postJson(url, body) {
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf,
      },
      body: JSON.stringify(body),
      credentials: "same-origin",
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok || !data.ok) {
          throw new Error((data && data.error) || "Save failed");
        }
        return data;
      });
    });
  }

  root.querySelectorAll("[data-notify-field]").forEach(function (input) {
    input.addEventListener("change", function () {
      var field = input.getAttribute("data-notify-field");
      var value = !!input.checked;
      if (notifyStatus) notifyStatus.textContent = "Saving…";
      postJson(notifyUrl, { field: field, value: value })
        .then(function () {
          if (notifyStatus) notifyStatus.textContent = "Saved";
          setTimeout(function () {
            if (notifyStatus && notifyStatus.textContent === "Saved") {
              notifyStatus.textContent = "";
            }
          }, 1600);
        })
        .catch(function () {
          input.checked = !value;
          if (notifyStatus) notifyStatus.textContent = "Couldn't save — try again";
        });
    });
  });

  /* Custom niche select (same pattern as Product Finder) */
  function closeSelect(wrap) {
    if (!wrap) return;
    wrap.classList.remove("is-open");
    var menu = wrap.querySelector(".cat-select__menu");
    var trigger = wrap.querySelector(".cat-select__trigger");
    if (menu) menu.hidden = true;
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  }

  function closeAllSelects(except) {
    root.querySelectorAll("[data-cat-select].is-open").forEach(function (wrap) {
      if (wrap !== except) closeSelect(wrap);
    });
  }

  function saveNiche(slug) {
    if (nicheStatus) nicheStatus.textContent = "Saving…";
    postJson(nicheUrl, { niche: slug })
      .then(function () {
        if (nicheStatus) nicheStatus.textContent = "Saved";
        setTimeout(function () {
          if (nicheStatus && nicheStatus.textContent === "Saved") {
            nicheStatus.textContent = "";
          }
        }, 1600);
      })
      .catch(function () {
        if (nicheStatus) nicheStatus.textContent = "Couldn't save — try again";
      });
  }

  root.querySelectorAll("[data-cat-select]").forEach(function (wrap) {
    var trigger = wrap.querySelector(".cat-select__trigger");
    var menu = wrap.querySelector(".cat-select__menu");
    var native = wrap.querySelector(".cat-select__native");
    var valueEl = wrap.querySelector(".cat-select__value");
    if (!trigger || !menu) return;

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      var open = wrap.classList.contains("is-open");
      closeAllSelects();
      if (!open) {
        wrap.classList.add("is-open");
        menu.hidden = false;
        trigger.setAttribute("aria-expanded", "true");
      }
    });

    menu.addEventListener("click", function (e) {
      var option = e.target.closest("[role='option']");
      if (!option) return;
      var value = option.getAttribute("data-value") || "";
      var label = option.textContent.trim();
      if (native) native.value = value;
      if (valueEl) valueEl.textContent = label;
      menu.querySelectorAll("[role='option']").forEach(function (li) {
        var on = li === option;
        li.classList.toggle("is-selected", on);
        if (on) li.setAttribute("aria-selected", "true");
        else li.removeAttribute("aria-selected");
      });
      closeSelect(wrap);
      if (wrap.hasAttribute("data-st-niche")) saveNiche(value);
    });
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest("[data-cat-select]")) closeAllSelects();
  });

  /* Delete account confirm — must type email */
  var confirm = root.querySelector("[data-st-confirm]");
  var confirmInput = root.querySelector("[data-st-confirm-input]");
  var confirmSubmit = root.querySelector("[data-st-confirm-submit]");
  var openBtn = root.querySelector("[data-st-delete-open]");

  function openConfirm() {
    if (!confirm) return;
    confirm.hidden = false;
    document.body.style.overflow = "hidden";
    if (confirmInput) {
      confirmInput.value = "";
      confirmInput.focus();
    }
    syncConfirm();
  }

  function closeConfirm() {
    if (!confirm) return;
    confirm.hidden = true;
    document.body.style.overflow = "";
  }

  function syncConfirm() {
    if (!confirmInput || !confirmSubmit) return;
    var expected = (confirmInput.getAttribute("data-expected") || "").trim().toLowerCase();
    var typed = (confirmInput.value || "").trim().toLowerCase();
    confirmSubmit.disabled = !expected || typed !== expected;
  }

  if (openBtn) openBtn.addEventListener("click", openConfirm);
  root.querySelectorAll("[data-st-confirm-cancel]").forEach(function (btn) {
    btn.addEventListener("click", closeConfirm);
  });
  if (confirmInput) confirmInput.addEventListener("input", syncConfirm);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeAllSelects();
      closeConfirm();
    }
  });
})();
