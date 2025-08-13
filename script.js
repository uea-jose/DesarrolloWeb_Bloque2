console.log("funcionando!");

// === REFERENCIAS CLAVE ===
const formulario = document.querySelector("#formulario");
const btnEnviar = document.querySelector("#btnEnviar");
const btnCargando = document.querySelector("#btnCargando");
const toast = document.querySelector(".toast");

// === EMAIL ===
const emailInput = document.getElementById("inputEmail");
const emailFeedback = document.getElementById("emailHelp");

const sugerencias = {
  "gmal.com": "gmail.com",
  "gmial.com": "gmail.com",
  "hotnail.com": "hotmail.com",
  "hotmial.com": "hotmail.com",
  "yahho.com": "yahoo.com",
  "yaho.com": "yahoo.com",
};

emailInput.addEventListener("input", () => {
  const value = emailInput.value.trim();
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const partes = value.split("@");

  if (partes.length === 2) {
    const usuario = partes[0];
    const dominio = partes[1].toLowerCase();

    if (sugerencias[dominio]) {
      const sugerido = `${usuario}@${sugerencias[dominio]}`;
      emailFeedback.innerHTML = `<span class="text-danger">¿Quisiste decir <strong>${sugerido}</strong>?</span>`;
      emailInput.classList.add("is-invalid");
      emailInput.classList.remove("is-valid");
      return;
    }
  }

  if (emailPattern.test(value)) {
    emailFeedback.textContent = "Correo válido";
    emailFeedback.classList.add("text-success");
    emailFeedback.classList.remove("text-danger");
    emailInput.classList.add("is-valid");
    emailInput.classList.remove("is-invalid");
  } else {
    emailFeedback.textContent = "Correo no válido";
    emailFeedback.classList.add("text-danger");
    emailFeedback.classList.remove("text-success");
    emailInput.classList.add("is-invalid");
    emailInput.classList.remove("is-valid");
  }
});

// === CONTRASEÑA ===
const passwordInput = document.getElementById("inputPassword");
const passwordFeedback = document.getElementById("contrasenaFeedback");

const reqMayusMinus = document.getElementById("req-mayus-minus");
const reqNumero = document.getElementById("req-numero");
const reqLongitud = document.getElementById("req-longitud");
const reqSimbolo = document.getElementById("req-simbolo");

const regexPassword = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;

passwordInput.addEventListener("input", () => {
  const valor = passwordInput.value;

  const tieneMayus = /[A-Z]/.test(valor);
  const tieneMinus = /[a-z]/.test(valor);
  const tieneNumero = /\d/.test(valor);
  const tieneLongitud = valor.length >= 8;
  const tieneSimbolo = /[\W_]/.test(valor);

  if (tieneMayus && tieneMinus) {
    reqMayusMinus.textContent = "✔️ Mayúsculas y minúsculas";
    reqMayusMinus.classList.add("text-success");
    reqMayusMinus.classList.remove("text-danger");
  } else {
    reqMayusMinus.textContent = "❌ Mayúsculas y minúsculas";
    reqMayusMinus.classList.add("text-danger");
    reqMayusMinus.classList.remove("text-success");
  }

  if (tieneNumero) {
    reqNumero.textContent = "✔️ Número (0-9)";
    reqNumero.classList.add("text-success");
    reqNumero.classList.remove("text-danger");
  } else {
    reqNumero.textContent = "❌ Número (0-9)";
    reqNumero.classList.add("text-danger");
    reqNumero.classList.remove("text-success");
  }

  if (tieneLongitud) {
    reqLongitud.textContent = "✔️ 8 caracteres";
    reqLongitud.classList.add("text-success");
    reqLongitud.classList.remove("text-danger");
  } else {
    reqLongitud.textContent = "❌ 8 caracteres";
    reqLongitud.classList.add("text-danger");
    reqLongitud.classList.remove("text-success");
  }

  if (tieneSimbolo) {
    reqSimbolo.textContent = "✔️ Al menos un símbolo o carácter especial";
    reqSimbolo.classList.add("text-success");
    reqSimbolo.classList.remove("text-danger");
  } else {
    reqSimbolo.textContent = "❌ Al menos un símbolo o carácter especial";
    reqSimbolo.classList.add("text-danger");
    reqSimbolo.classList.remove("text-success");
  }

  if (regexPassword.test(valor)) {
    passwordInput.classList.add("is-valid");
    passwordInput.classList.remove("is-invalid");
    passwordFeedback.textContent = "";
  } else {
    passwordInput.classList.add("is-invalid");
    passwordInput.classList.remove("is-valid");
    passwordFeedback.textContent = "La contraseña no cumple con los requisitos.";
  }
});
// === REPETIR CONTRASEÑA ===
const confirmarInput = document.getElementById("confirmarContrasena");
const confirmarFeedback = document.getElementById("confirmarContrasenaFeedback");

// Función para validar que ambas contraseñas coincidan
function validarRepetirContrasena() {
  const passwordVal = passwordInput.value;
  const confirmarVal = confirmarInput.value;

  // Si está vacío, no mostrar aún el error
  if (confirmarVal === "") {
    confirmarFeedback.textContent = "";
    confirmarInput.classList.remove("is-invalid");
    return;
  }

  if (passwordVal !== confirmarVal) {
    confirmarFeedback.textContent = "Las contraseñas no coinciden.";
    confirmarInput.classList.add("is-invalid");
    confirmarInput.classList.remove("is-valid");
  } else {
    confirmarFeedback.textContent = "";
    confirmarInput.classList.remove("is-invalid");
    confirmarInput.classList.add("is-valid");
  }
}

// Escuchar cambios tanto en contraseña como en confirmar
passwordInput.addEventListener("input", validarRepetirContrasena);
confirmarInput.addEventListener("input", validarRepetirContrasena);

// === SUBMIT FINAL ===
formulario.addEventListener("submit", (e) => {
  e.preventDefault();

  const emailValido = emailInput.classList.contains("is-valid");
  const passwordValida = passwordInput.classList.contains("is-valid");

  if (!emailValido || !passwordValida) {
    alert("Revisa los campos marcados en rojo.");
    return;
  }

  btnEnviar.classList.add("d-none");
  btnCargando.classList.remove("d-none");

  const datos = new FormData(formulario);
  console.log("email:", datos.get("campoEmail"));
  console.log("password:", datos.get("campoPassword"));

  window.setTimeout(() => {
    btnEnviar.classList.remove("d-none");
    btnCargando.classList.add("d-none");

    formulario.reset();
    emailInput.classList.remove("is-valid", "is-invalid");
    passwordInput.classList.remove("is-valid", "is-invalid");
    emailFeedback.textContent = "No compartiremos su correo electrónico.";
    emailFeedback.classList.remove("text-success", "text-danger");

    [reqMayusMinus, reqNumero, reqLongitud, reqSimbolo].forEach((li) => {
      li.classList.remove("text-success");
      li.classList.add("text-danger");
      li.textContent = "❌ " + li.textContent.replace(/^✔️ |^❌ /, "");
    });

    const eventoToast = new bootstrap.Toast(toast);
    eventoToast.show();
  }, 1000);
});
