console.log("funcionando!");

// =======================
//  REFERENCIAS CLAVE
// =======================
const formulario   = document.querySelector("#formulario");
const btnEnviar    = document.querySelector("#btnEnviar");
const btnCargando  = document.querySelector("#btnCargando");
const toast        = document.querySelector(".toast");

// =======================
//  EMAIL
// =======================
const emailInput    = document.getElementById("inputEmail");
const emailFeedback = document.getElementById("emailHelp");

// Correcciones comunes de dominio
const sugerencias = {
  "gmal.com":   "gmail.com",
  "gmial.com":  "gmail.com",
  "hotnail.com":"hotmail.com",
  "hotmial.com":"hotmail.com",
  "yahho.com":  "yahoo.com",
  "yaho.com":   "yahoo.com",
};

// Validador “moderno” (sin espacios, sin dobles puntos, con TLD de 2-24)
function isValidEmail(email){
  if (!email || email.includes(" ")) return false;
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,24}$/i.test(email)) return false;
  if (email.includes("..")) return false;
  const [local, domain] = email.split("@");
  if (!local || !domain) return false;
  if (!/^[A-Za-z0-9.-]+$/.test(domain)) return false;
  if (domain.startsWith("-") || domain.endsWith("-")) return false;
  if (!domain.includes(".")) return false;
  return true;
}

emailInput.addEventListener("input", () => {
  const value   = emailInput.value.trim();
  const partes  = value.split("@");

  // Sugerir dominios si hay error típico
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

  // Validación
  if (isValidEmail(value)) {
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

// =======================
//  CONTRASEÑA con POPOVER dinámico
// =======================
// =======================
//  CONTRASEÑA con POPOVER dinámico
// =======================
const passwordInput    = document.getElementById("inputPassword");
const passwordFeedback = document.getElementById("contrasenaFeedback");

// Reglas
const reglas = {
  upper:  s => /[A-Z]/.test(s),
  lower:  s => /[a-z]/.test(s),
  digit:  s => /\d/.test(s),
  symbol: s => /[!@#$%^&*()_\-+=\[{\]};:'",.<>/?\\|`~]/.test(s), // símbolos recomendados
  length: s => s.length >= 8
};

// Crea popover Bootstrap (mensaje emergente)
const passPopover = new bootstrap.Popover(passwordInput, {
  container: 'body',
  html: true,
  sanitize: false // mostramos una lista HTML
});

// Texto de pendientes
const etiquetas = {
  upper:  'una <strong>mayúscula</strong> (A-Z)',
  lower:  'una <strong>minúscula</strong> (a-z)',
  digit:  'un <strong>número</strong> (0-9)',
  symbol: 'un <strong>símbolo</strong> (por ej. ! @ # $ % & …)',
  length: '<strong>8 caracteres</strong> mínimo'
};

function faltantes(val){
  return Object.keys(reglas).filter(k => !reglas[k](val));
}

function renderLista(keys){
  if (!keys.length) return '';
  const li = keys.map(k => `<li>Te falta ${etiquetas[k]}.</li>`).join('');
  return `<ul class="mb-0 ps-3">${li}</ul>`;
}

function actualizarPasswordUI(){
  const val = passwordInput.value;
  const missing = faltantes(val);

  if (val.length === 0){
    passwordInput.classList.remove("is-valid","is-invalid");
    passPopover.hide();
    return;
  }

  if (missing.length === 0){
    passwordInput.classList.add("is-valid");
    passwordInput.classList.remove("is-invalid");
    passPopover.hide();
    passwordFeedback.textContent = "";
  } else {
    passwordInput.classList.add("is-invalid");
    passwordInput.classList.remove("is-valid");
    passwordFeedback.textContent = "La contraseña no cumple con los requisitos.";
    // Actualiza el popover con lo que falta
    const bodyHtml = renderLista(missing);
    passPopover.setContent({
      '.popover-header': 'Requisitos pendientes',
      '.popover-body':  bodyHtml
    });
    passPopover.show();
  }

  // Mantén sincronizada la confirmación
  validarRepetirContrasena?.();
}

passwordInput.addEventListener("input", actualizarPasswordUI);
passwordInput.addEventListener("focus", actualizarPasswordUI);
passwordInput.addEventListener("blur",  ()=> passPopover.hide());

// =======================
//  REPETIR CONTRASEÑA
// =======================
const confirmarInput    = document.getElementById("confirmarContrasena");
const confirmarFeedback = document.getElementById("confirmarContrasenaFeedback");

function validarRepetirContrasena() {
  const passwordVal  = passwordInput.value;
  const confirmarVal = confirmarInput.value;

  if (confirmarVal === "") {
    confirmarFeedback.textContent = "";
    confirmarInput.classList.remove("is-invalid", "is-valid");
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

passwordInput.addEventListener("input", validarRepetirContrasena);
confirmarInput.addEventListener("input", validarRepetirContrasena);

// =======================
//  OJITO MOSTRAR/OCULTAR
//  (click para alternar + mantener pulsado)
// =======================
function attachEyeToggle(inputId, btnId){
  const input = document.getElementById(inputId);
  const btn   = document.getElementById(btnId);
  if(!input || !btn) return;

  const icon = btn.querySelector('i');

  // Click: alterna mostrar/ocultar
  btn.addEventListener('click', (e)=>{
    e.preventDefault();
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    if(icon){
      icon.classList.toggle('bi-eye', isHidden);
      icon.classList.toggle('bi-eye-slash', !isHidden);
    }
  });

  // Mantener pulsado para ver (opcional y no molesta al toggle)
  btn.addEventListener('mousedown', ()=>{ input.type = 'text'; });
  btn.addEventListener('mouseup',   ()=>{ if(icon && !icon.classList.contains('bi-eye')) input.type = 'password'; });
  btn.addEventListener('mouseleave',()=>{ if(icon && !icon.classList.contains('bi-eye')) input.type = 'password'; });
}

// Activa en los dos campos
attachEyeToggle('inputPassword','togglePass');
attachEyeToggle('confirmarContrasena','togglePass2');

// =======================
//  SUBMIT FINAL
// =======================
const termsCheck = document.getElementById("inputCheck");

formulario.addEventListener("submit", (e) => {
  e.preventDefault();

  const emailValido     = isValidEmail(emailInput.value.trim());
  const passwordValida  = passwordInput.classList.contains("is-valid");
  const repetirOK       = confirmarInput.value === passwordInput.value && confirmarInput.value.length > 0;
  const condicionesOK   = !!termsCheck?.checked;

  // Estados visuales finales
  if (!emailValido){
    emailInput.classList.add("is-invalid");
    emailInput.classList.remove("is-valid");
  }
  if (!passwordValida){
    passwordInput.classList.add("is-invalid");
    passwordInput.classList.remove("is-valid");
  }
  if (!repetirOK){
    confirmarInput.classList.add("is-invalid");
    confirmarInput.classList.remove("is-valid");
    confirmarFeedback.textContent = "Las contraseñas no coinciden.";
  }
  if (!condicionesOK){
    termsCheck.classList.add("is-invalid");
  } else {
    termsCheck.classList.remove("is-invalid");
  }

  if (!emailValido || !passwordValida || !repetirOK || !condicionesOK) {
    alert("Revisa los campos marcados en rojo.");
    return;
  }

  // Simulación de envío
  btnEnviar.classList.add("d-none");
  btnCargando.classList.remove("d-none");

  const datos = new FormData(formulario);
  console.log("email:", datos.get("campoEmail"));
  console.log("password:", datos.get("campoPassword"));

  window.setTimeout(() => {
    btnEnviar.classList.remove("d-none");
    btnCargando.classList.add("d-none");

    // Reset
    formulario.reset();
    [emailInput, passwordInput, confirmarInput].forEach(el=>{
      el.classList.remove("is-valid","is-invalid");
    });
    termsCheck.classList.remove("is-invalid");

    emailFeedback.textContent = "No compartiremos su correo electrónico.";
    emailFeedback.classList.remove("text-success","text-danger");

    const eventoToast = new bootstrap.Toast(toast);
    eventoToast.show();
  }, 1000);
});
