// script_masculinos.js — DOM-driven como femeninos; +1 = reservar (resta stock), -1 = devolver (suma stock)

/********* ESTADO *********/
let carrito = [];                 // [{id,titulo,precio,cantidad,gender}]
let stock   = {};                 // slug -> stock visible
let precios = {};                 // slug -> precio
let nombres = {};                 // slug -> nombre visible

/********* DOM *********/
const carritoUL      = document.querySelector("#carrito");
const templateItem   = document.querySelector("#templateItem");
const footer         = document.querySelector("#footer");
const templateFooter = document.querySelector("#templateFooter");

/********* UTIL: formato moneda *********/
const money = (n) =>
  Number(n).toLocaleString("es-EC", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

/********* Cache inicial desde el HTML *********/
document.querySelectorAll(".card button[data-slug]").forEach((btn) => {
  const slug = btn.dataset.slug;
  precios[slug] = Number(btn.dataset.precio);
  nombres[slug] = btn.dataset.name || slug;
});
document.querySelectorAll(".stock-count[data-slug]").forEach((s) => {
  stock[s.dataset.slug] = Number(s.textContent) || 0;
});

/********* Descripción automática (opcional) *********/
function autoDesc({ name, price }) {
  const base = [
    "Amaderada y elegante",
    price >= 600
      ? "Gama alta"
      : price >= 300
      ? "Excelente relación calidad/precio"
      : "Opción accesible",
    "Fragancia versátil para todo el día",
    "Entrega inmediata",
  ];
  const n = (name || "").toLowerCase();
  if (n.includes("cedar") || n.includes("cedro")) base.unshift("Notas de cedro");
  if (n.includes("leather") || n.includes("cuero")) base.unshift("Acentos de cuero");
  return base.slice(0, 4);
}
document.querySelectorAll(".card").forEach((card) => {
  const btn = card.querySelector("button[data-slug]");
  const ul = card.querySelector(".desc");
  if (!btn || !ul) return;
  const title = btn.dataset.name || card.querySelector(".card-header .card-title-text")?.textContent || btn.dataset.slug;
  const price = Number(btn.dataset.precio);
  ul.innerHTML = autoDesc({ name: title, price }).map((t) => `<li>${t}</li>`).join("");
});

/********* API: stock *********/
async function applyStock(slug, delta) {
  try {
    const res = await fetch("/api/stock/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug, delta }),
    });

    if (res.status === 409) {
      const data = await res.json();
      updateStockUI(slug, data.stock);
      alert(`No hay más stock de "${nombres[slug] || slug}".`);
      return { ok: false };
    }

    const data = await res.json();
    if (data.ok) {
      updateStockUI(slug, data.stock);
      return { ok: true };
    }
    alert("No se pudo actualizar el stock.");
    return { ok: false };
  } catch (err) {
    console.error(err);
    alert("Error de red al actualizar el stock.");
    return { ok: false };
  }
}

/********* Stock UI *********/
function updateStockUI(slug, value) {
  if (typeof value === "number") stock[slug] = value;

  const count = document.querySelector(`.stock-count[data-slug="${slug}"]`);
  if (count) count.textContent = stock[slug] ?? 0;

  const btn = document.querySelector(`button[data-slug="${slug}"]`);
  if (btn) {
    const agotado = (stock[slug] ?? 0) <= 0;
    btn.disabled = agotado;
    btn.textContent = agotado ? "Agotado" : "Agregar";
    btn.classList.toggle("disabled", agotado);
  }
}
// Sincroniza botones al cargar (por si alguno está en 0)
Object.keys(stock).forEach((slug) => updateStockUI(slug));

/********* Pintar carrito *********/
function pintarFooter() {
  footer.textContent = "";
  const total = carrito.reduce((acc, it) => acc + it.precio * it.cantidad, 0);
  const clone = templateFooter.content.cloneNode(true);
  clone.querySelector("p span").textContent = money(total);
  footer.appendChild(clone);
}

function pintarCarrito() {
  carritoUL.textContent = "";
  const frag = document.createDocumentFragment();

  carrito.forEach((it) => {
    const clone = templateItem.content.cloneNode(true);

    // encabezado
    clone.querySelector(".rounded-pill").textContent = it.cantidad;
    clone.querySelector(".item-header .lead").textContent = (it.titulo || it.id).toUpperCase();
    clone.querySelector("div .lead span").textContent = money(it.precio * it.cantidad);

    clone.querySelector(".btn-success").dataset.id = it.id;
    clone.querySelector(".btn-danger").dataset.id = it.id;

    frag.appendChild(clone);
  });

  carritoUL.appendChild(frag);
  pintarFooter();
}

/********* Eventos *********/
document.addEventListener("click", async (e) => {
  // Agregar desde card
  if (e.target.matches(".card button[data-slug]")) {
    const slug = e.target.dataset.slug;
    const ok = (await applyStock(slug, +1)).ok; // +1 = reservar (resta stock)
    if (!ok) return;

    const idx = carrito.findIndex((x) => x.id === slug);
    if (idx === -1) {
      carrito.push({
        id: slug,
        titulo: nombres[slug] || slug,
        precio: precios[slug],
        cantidad: 1,
        gender: "M",
      });
    } else {
      carrito[idx].cantidad++;
    }
    pintarCarrito();
  }

  // + en carrito
  if (e.target.matches(".list-group-item .btn-success")) {
    const id = e.target.dataset.id;
    const ok = (await applyStock(id, +1)).ok; // reserva otra unidad
    if (!ok) return;
    carrito = carrito.map((it) => (it.id === id ? { ...it, cantidad: it.cantidad + 1 } : it));
    pintarCarrito();
  }

  // - en carrito
  if (e.target.matches(".list-group-item .btn-danger")) {
    const id = e.target.dataset.id;
    let decreased = false;
    carrito = carrito
      .map((it) => {
        if (it.id === id && it.cantidad > 0) {
          it.cantidad--;
          decreased = true;
        }
        return it;
      })
      .filter((it) => it.cantidad > 0);

    if (decreased) await applyStock(id, -1); // devolver unidad
    pintarCarrito();
  }

  // Finalizar
  if (e.target.matches("#finalizar")) {
    if (carrito.length) alert("¡Gracias por tu compra!");
  }
});