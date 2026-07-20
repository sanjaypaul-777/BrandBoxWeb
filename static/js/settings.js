/**
 * Settings — notification toggles.
 */
(function () {
  var root = document.querySelector("[data-settings]");
  if (!root) return;

  var csrf =
    (document.querySelector("[name=csrfmiddlewaretoken]") &&
      document.querySelector("[name=csrfmiddlewaretoken]").value) || "";
  var notifyUrl = root.getAttribute("data-notify-url") || "";
  var notifyStatus = root.querySelector("[data-notify-status]");

  function postJson(url, body) {
    return fetch(url, {
      method:"POST",
      headers: {"Content-Type":"application/json","X-CSRFToken": csrf,
      },
      body: JSON.stringify(body),
      credentials:"same-origin",
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
      if (notifyStatus) notifyStatus.textContent ="Saving…";
      postJson(notifyUrl, { field: field, value: value })
        .then(function () {
          if (notifyStatus) notifyStatus.textContent ="Saved";
          setTimeout(function () {
            if (notifyStatus && notifyStatus.textContent === "Saved") {
              notifyStatus.textContent ="";
            }
          }, 1600);
        })
        .catch(function () {
          input.checked = !value;
          if (notifyStatus) notifyStatus.textContent ="Couldn't save — try again";
        });
    });
  });
})();
