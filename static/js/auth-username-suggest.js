/**
 * auth-username-suggest.js — Light suggestion lists under auth email/name fields.
 * Uses fixed coords from the input (absolute+parent was landing too far down on
 * contact / affiliate / signup layouts).
 */
(function () {
  "use strict";

  var STORAGE_PREFIX = "brandbox.auth.suggest.";
  var SHARED_LOGIN_KEY = STORAGE_PREFIX + "loginId";
  var MAX_ITEMS = 8;

  function isLoginLike(input) {
    var name = (input.getAttribute("name") || "").toLowerCase();
    var id = (input.id || "").toLowerCase();
    var type = (input.type || "").toLowerCase();
    return (
      type === "email" ||
      name === "email" ||
      name === "username" ||
      id === "id_email" ||
      id === "id_username" ||
      id === "email"
    );
  }

  function storageKey(input) {
    if (isLoginLike(input)) return SHARED_LOGIN_KEY;
    var key = input.getAttribute("name") || input.id || "field";
    return STORAGE_PREFIX + key;
  }

  function loadIds(input) {
    try {
      var raw = localStorage.getItem(storageKey(input));
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list)
        ? list.filter(function (v) {
            return typeof v === "string" && v.trim();
          })
        : [];
    } catch (e) {
      return [];
    }
  }

  function saveId(input, value) {
    var id = String(value || "").trim();
    if (!id || id.length < 2) return;
    var next = [id].concat(
      loadIds(input).filter(function (v) {
        return v.toLowerCase() !== id.toLowerCase();
      })
    );
    try {
      localStorage.setItem(storageKey(input), JSON.stringify(next.slice(0, MAX_ITEMS)));
    } catch (e) {}
  }

  function matches(input, query) {
    var q = String(query || "").trim().toLowerCase();
    var all = loadIds(input);
    if (!q) return all.slice(0, MAX_ITEMS);
    return all.filter(function (v) {
      return v.toLowerCase().indexOf(q) !== -1;
    });
  }

  function shouldEnhance(input) {
    if (!input || input.dataset.authSuggest === "1") return false;
    if (input.closest(".auth-suggest, .auth-decoy, .brandbox-honeypot")) return false;
    if (input.type === "password" || input.type === "hidden" || input.type === "checkbox") {
      return false;
    }
    if (input.type === "url" || input.type === "tel" || input.type === "number") {
      return false;
    }
    /* Email / username / name only — skip long misc text fields on affiliate */
    var name = (input.getAttribute("name") || "").toLowerCase();
    var id = (input.id || "").toLowerCase();
    if (isLoginLike(input)) return true;
    if (
      name === "name" ||
      name === "first_name" ||
      name === "last_name" ||
      id === "id_name" ||
      id === "id_first_name" ||
      id === "id_last_name"
    ) {
      return true;
    }
    return false;
  }

  function enhance(input) {
    if (!shouldEnhance(input)) return;

    input.dataset.authSuggest = "1";
    input.setAttribute("autocomplete", "off");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("data-lpignore", "true");
    input.setAttribute("data-1p-ignore", "true");
    input.setAttribute("data-bwignore", "true");

    var wrap = document.createElement("div");
    wrap.className = "auth-suggest";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);

    var listId = (input.id || "auth-field") + "-suggest";
    input.setAttribute("aria-controls", listId);

    var list = document.createElement("ul");
    list.className = "auth-suggest__list";
    list.id = listId;
    list.setAttribute("role", "listbox");
    list.hidden = true;
    /* Body + fixed = always under the field, even inside grid/card layouts */
    document.body.appendChild(list);

    var activeIndex = -1;

    function place() {
      var rect = input.getBoundingClientRect();
      list.style.position = "fixed";
      list.style.left = Math.round(rect.left) + "px";
      list.style.top = Math.round(rect.bottom + 6) + "px";
      list.style.width = Math.round(rect.width) + "px";
      list.style.right = "auto";
      list.style.zIndex = "10000";
    }

    function close() {
      list.hidden = true;
      list.innerHTML = "";
      activeIndex = -1;
      input.removeAttribute("aria-activedescendant");
      input.setAttribute("aria-expanded", "false");
      window.removeEventListener("scroll", onReposition, true);
      window.removeEventListener("resize", onReposition);
    }

    function onReposition() {
      if (list.hidden) return;
      place();
    }

    function open(items) {
      list.innerHTML = "";
      activeIndex = -1;
      if (!items.length) {
        close();
        return;
      }
      items.forEach(function (value, i) {
        var li = document.createElement("li");
        li.className = "auth-suggest__item";
        li.setAttribute("role", "option");
        li.id = listId + "-opt-" + i;
        li.textContent = value;
        li.addEventListener("mousedown", function (e) {
          e.preventDefault();
          input.value = value;
          close();
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.focus();
        });
        list.appendChild(li);
      });
      place();
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
      window.addEventListener("scroll", onReposition, true);
      window.addEventListener("resize", onReposition);
    }

    function refresh() {
      open(matches(input, input.value));
    }

    function setActive(next) {
      var opts = list.querySelectorAll(".auth-suggest__item");
      if (!opts.length) return;
      activeIndex = (next + opts.length) % opts.length;
      opts.forEach(function (el, i) {
        var on = i === activeIndex;
        el.classList.toggle("is-active", on);
        el.setAttribute("aria-selected", on ? "true" : "false");
      });
      input.setAttribute("aria-activedescendant", opts[activeIndex].id);
    }

    input.setAttribute("aria-expanded", "false");
    input.addEventListener("focus", refresh);
    input.addEventListener("input", refresh);
    input.addEventListener("keydown", function (e) {
      if (list.hidden) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActive(activeIndex + 1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActive(activeIndex - 1);
      } else if (e.key === "Enter" && activeIndex >= 0) {
        var opts = list.querySelectorAll(".auth-suggest__item");
        if (opts[activeIndex]) {
          e.preventDefault();
          input.value = opts[activeIndex].textContent;
          close();
        }
      } else if (e.key === "Escape") {
        close();
      }
    });
    input.addEventListener("blur", function () {
      window.setTimeout(close, 120);
    });

    var form = input.form;
    if (form && !form.dataset.authSuggestBound) {
      form.dataset.authSuggestBound = "1";
      form.setAttribute("autocomplete", "off");
      form.addEventListener("submit", function () {
        form.querySelectorAll("input[data-auth-suggest='1']").forEach(function (el) {
          saveId(el, el.value);
        });
      });
    }
  }

  function migrateOldLoginKeys() {
    try {
      if (localStorage.getItem(SHARED_LOGIN_KEY)) return;
      var legacy = [];
      ["brandbox.auth.loginIds"].forEach(function (fullKey) {
        var raw = localStorage.getItem(fullKey);
        if (!raw) return;
        var list = JSON.parse(raw);
        if (Array.isArray(list)) legacy = legacy.concat(list);
      });
      ["username", "email", "id_username", "id_email"].forEach(function (k) {
        var raw = localStorage.getItem(STORAGE_PREFIX + k);
        if (!raw) return;
        var list = JSON.parse(raw);
        if (Array.isArray(list)) legacy = legacy.concat(list);
      });
      var seen = {};
      var merged = [];
      legacy.forEach(function (v) {
        if (typeof v !== "string" || !v.trim()) return;
        var key = v.toLowerCase();
        if (seen[key]) return;
        seen[key] = true;
        merged.push(v.trim());
      });
      if (merged.length) {
        localStorage.setItem(SHARED_LOGIN_KEY, JSON.stringify(merged.slice(0, MAX_ITEMS)));
      }
    } catch (e) {}
  }

  function init() {
    var root = document.querySelector(".auth-page");
    if (!root) return;
    migrateOldLoginKeys();
    root
      .querySelectorAll(
        '.auth-form input[type="email"], .auth-form input[type="text"], .auth-form input:not([type])'
      )
      .forEach(enhance);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
