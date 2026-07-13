/**
 * My Imports — edit / remove / push via Django → Node APIs.
 */
(function () {
  var root = document.querySelector("[data-my-imports]");
  if (!root) return;

  var csrf = root.getAttribute("data-csrf") || "";
  var apiBase = root.getAttribute("data-api-base") || "/dashboard/api/imports/";
  var toast = root.querySelector("[data-imp-toast]");
  var toastMsg = root.querySelector("[data-imp-toast-msg]");
  var dismiss = root.querySelector("[data-imp-toast-dismiss]");
  var list = root.querySelector("[data-imp-list]");
  var viewToggle = root.querySelector("[data-imp-view-toggle]");

  function detailUrl(id) {
    return apiBase.replace(/\/?$/, "/") + encodeURIComponent(id) + "/";
  }

  function showToast(message, tone) {
    if (!toast || !toastMsg) return;
    toastMsg.textContent = message;
    toast.className = "imp-toast imp-toast--" + (tone || "success");
    toast.hidden = false;
  }

  if (dismiss) {
    dismiss.addEventListener("click", function () {
      if (toast) toast.hidden = true;
    });
  }

  function setView(view) {
    if (!list || !viewToggle) return;
    list.setAttribute("data-view", view);
    viewToggle.querySelectorAll("button[data-view]").forEach(function (btn) {
      var on = btn.getAttribute("data-view") === view;
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  if (viewToggle) {
    viewToggle.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-view]");
      if (!btn) return;
      setView(btn.getAttribute("data-view"));
    });
  }

  function api(id, method, body) {
    return fetch(detailUrl(id), {
      method: method,
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf,
      },
      body: body ? JSON.stringify(body) : undefined,
    }).then(function (r) {
      return r.json().then(function (data) {
        return { ok: r.ok && data.ok !== false, status: r.status, data: data };
      });
    });
  }

  root.addEventListener("click", function (e) {
    var editBtn = e.target.closest("[data-imp-edit]");
    var cancelBtn = e.target.closest("[data-imp-cancel]");
    var saveBtn = e.target.closest("[data-imp-save]");
    var removeBtn = e.target.closest("[data-imp-remove]");
    var pushBtn = e.target.closest("[data-imp-push]");
    var row = e.target.closest("[data-imp-row]");
    if (!row) return;

    var importId = row.getAttribute("data-import-id");
    var view = row.querySelector("[data-imp-view]");
    var form = row.querySelector("[data-imp-form]");
    var actions = row.querySelector("[data-imp-actions]");

    if (editBtn && view && form) {
      view.hidden = true;
      form.hidden = false;
      if (actions) actions.hidden = true;
      var first = form.querySelector("input");
      if (first) first.focus();
      return;
    }

    if (cancelBtn && view && form) {
      form.hidden = true;
      view.hidden = false;
      if (actions) actions.hidden = false;
      return;
    }

    if (saveBtn && form && importId) {
      var title = (form.querySelector("[data-imp-title]") || {}).value || "";
      var sell = (form.querySelector("[data-imp-sell]") || {}).value || "";
      var compare = (form.querySelector("[data-imp-compare]") || {}).value || "";
      saveBtn.disabled = true;
      api(importId, "PATCH", {
        title: title,
        sellPrice: sell,
        compareAtPrice: compare || null,
      })
        .then(function (res) {
          saveBtn.disabled = false;
          if (!res.ok) {
            showToast(
              (res.data && (res.data.message || res.data.error)) || "Save failed",
              "error"
            );
            return;
          }
          var imp = (res.data && res.data.import) || {};
          var titleEl = view && view.querySelector(".imp-row__title");
          if (titleEl && imp.title) titleEl.textContent = imp.title;
          var sellLabel = view && view.querySelector("[data-imp-sell-label]");
          if (sellLabel && imp.sellPrice != null && imp.sellPrice !== "") {
            sellLabel.textContent = "$" + Number(imp.sellPrice).toFixed(2);
          }
          var sellInput = form.querySelector("[data-imp-sell]");
          if (sellInput && imp.sellPrice != null && imp.sellPrice !== "") {
            sellInput.value = Number(imp.sellPrice).toFixed(2);
          }
          var compareLabel = view && view.querySelector("[data-imp-compare-label]");
          var compareWrap = view && view.querySelector("[data-imp-compare-wrap]");
          var compareInput = form.querySelector("[data-imp-compare]");
          if (imp.compareAtPrice != null && imp.compareAtPrice !== "") {
            var cmp = Number(imp.compareAtPrice).toFixed(2);
            if (compareLabel) compareLabel.textContent = "$" + cmp;
            if (compareWrap) compareWrap.hidden = false;
            if (compareInput) compareInput.value = cmp;
          } else {
            if (compareLabel) compareLabel.textContent = "";
            if (compareWrap) compareWrap.hidden = true;
            if (compareInput) compareInput.value = "";
          }
          var titleInput = form.querySelector("[data-imp-title]");
          if (titleInput && imp.title) titleInput.value = imp.title;
          form.hidden = true;
          if (view) view.hidden = false;
          if (actions) actions.hidden = false;
          showToast("Saved", "success");
        })
        .catch(function () {
          saveBtn.disabled = false;
          showToast("Save failed", "error");
        });
      return;
    }

    if (removeBtn && importId) {
      removeBtn.disabled = true;
      api(importId, "DELETE")
        .then(function (res) {
          if (!res.ok) {
            removeBtn.disabled = false;
            showToast(
              (res.data && (res.data.message || res.data.error)) || "Remove failed",
              "error"
            );
            return;
          }
          row.remove();
          showToast("Removed from your imports", "success");
          if (list && !list.querySelector("[data-imp-row]")) {
            window.location.reload();
          }
        })
        .catch(function () {
          removeBtn.disabled = false;
          showToast("Remove failed", "error");
        });
      return;
    }

    if (pushBtn && importId) {
      pushBtn.disabled = true;
      pushBtn.textContent = "Pushing…";
      api(importId, "POST", { action: "publish", publish: true })
        .then(function (res) {
          if (!res.ok) {
            pushBtn.disabled = false;
            pushBtn.textContent = "Push";
            showToast(
              (res.data && (res.data.message || res.data.error)) || "Push failed",
              "error"
            );
            return;
          }
          showToast("Pushed — now live in your store.", "success");
          row.remove();
          if (list && !list.querySelector("[data-imp-row]")) {
            window.location.reload();
          }
        })
        .catch(function () {
          pushBtn.disabled = false;
          pushBtn.textContent = "Push";
          showToast("Push failed", "error");
        });
    }
  });
})();
