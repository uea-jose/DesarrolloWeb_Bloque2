// app/static/script.js
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("form-registro");
  const pw1  = document.getElementById("password");
  const pw2  = document.getElementById("password2");
  const msg  = document.getElementById("pw-msg");
  const btn  = document.getElementById("btn-submit");

  // Si no estamos en la página de registro, salir
  if (!form || !pw1 || !pw2 || !msg || !btn) return;

  function setState(state, textOk = "Las contraseñas coinciden", textBad = "Las contraseñas no coinciden") {
    // Limpia
    [pw1, pw2].forEach(el => el.classList.remove("is-valid", "is-invalid"));

    if (state === "ok") {
      pw1.classList.add("is-valid");
      pw2.classList.add("is-valid");
      msg.textContent = textOk;
      msg.className = "small mt-1 text-success";
      btn.disabled = false;
    } else if (state === "bad") {
      pw1.classList.add("is-invalid");
      pw2.classList.add("is-invalid");
      msg.textContent = textBad;
      msg.className = "small mt-1 text-danger";
      btn.disabled = true;
    } else {
      msg.textContent = "Repite la contraseña exactamente";
      msg.className = "small mt-1 text-muted";
      btn.disabled = true;
    }
  }

  function validate() {
    const a = pw1.value.trim();
    const b = pw2.value.trim();

    if (!a || !b) { setState("neutral"); return; }
    setState(a === b ? "ok" : "bad");
  }

  pw1.addEventListener("input", validate);
  pw2.addEventListener("input", validate);

  form.addEventListener("submit", (e) => {
    const a = pw1.value.trim();
    const b = pw2.value.trim();
    if (!a || a !== b) {
      e.preventDefault();
      validate();
    }
  });

  // Estado inicial
  setState("neutral");
});
