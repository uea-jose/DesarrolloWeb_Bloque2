# -*- coding: utf-8 -*-
"""
Busca una imagen de "212 VIP Club" con ddgs evitando rate-limit:
- Prueba backends: html -> lite -> api
- Reintentos con backoff y pausas aleatorias
- Valida que la URL sea imagen y responda 200
- Recorta a cuadrado, guarda JPG y muestra miniatura
"""

import io, os, time, random
import requests
from PIL import Image
import matplotlib.pyplot as plt
from slugify import slugify

# NUEVO paquete
from ddgs import DDGS
from ddgs.exceptions import RatelimitException

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def _first_working_image(results, max_check=6):
    """Devuelve la primera URL que:
       - termina en .jpg/.jpeg/.png/.webp (antes de ?)
       - responde 200 y Content-Type imagen
    """
    sess = requests.Session()
    sess.headers.update({"User-Agent": UA})
    checked = 0
    for r in results:
        if checked >= max_check:
            break
        url = r.get("image") or r.get("thumbnail") or r.get("url")
        if not url:
            continue
        base = url.split("?")[0].lower()
        if not base.endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        try:
            # HEAD rápido; si el host no soporta HEAD, probamos GET corto
            h = sess.head(url, timeout=8, allow_redirects=True)
            ok = (h.status_code < 400) and ("image" in h.headers.get("Content-Type", ""))
            if not ok:
                g = sess.get(url, timeout=12, stream=True)
                ok = (g.status_code < 400) and ("image" in g.headers.get("Content-Type", ""))
                g.close()
            if ok:
                return url
        except Exception:
            pass
        finally:
            checked += 1
    return None

def ddg_images(query: str, backend: str, max_results: int = 8):
    """Wrapper de búsqueda para un backend concreto."""
    with DDGS() as ddgs:
        return list(ddgs.images(
            keywords=query,
            max_results=max_results,
            safesearch="moderate",
            region="es-es",
            backend=backend,
        ))

def find_image_url(query: str) -> str:
    """Intenta varios backends y reintentos para esquivar 403."""
    backends_order = ["html", "lite", "api"]
    # Hasta 2 rondas completas de backends con backoff
    for attempt in range(1, 3):
        for backend in backends_order:
            try:
                # menos resultados para reducir prob. de bloqueo
                results = ddg_images(query, backend=backend, max_results=6)
                url = _first_working_image(results, max_check=6)
                if url:
                    return url
            except RatelimitException:
                # pequeña pausa y probamos siguiente backend
                time.sleep(random.uniform(1.0, 2.5))
                continue
            except Exception:
                # cualquier otro error: intentar siguiente backend
                continue
        # backoff antes de otra ronda completa
        time.sleep(attempt * random.uniform(1.2, 2.8))
    raise RuntimeError("No se encontró una imagen adecuada (rate-limit o sin resultados).")

def download_image(url: str) -> Image.Image:
    sess = requests.Session()
    sess.headers.update({"User-Agent": UA, "Referer": "https://duckduckgo.com/"})
    resp = sess.get(url, timeout=20)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")

def crop_square(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))

def save_jpg(img: Image.Image, base_name: str, size_px: int = 256) -> str:
    img_small = img.resize((size_px, size_px), Image.LANCZOS)
    fname = f"{slugify(base_name)}.jpg"
    img_small.save(fname, "JPEG", quality=85, optimize=True, progressive=True)
    return fname

def main():
    query = "212 VIP Club perfume Carolina Herrera"
    print(f"Buscando imagen para: {query!r} ...")
    url = find_image_url(query)
    print("URL encontrada:", url)

    print("Descargando...")
    img = download_image(url)

    print("Recortando a cuadrado y guardando miniatura...")
    img_sq = crop_square(img)
    outfile = save_jpg(img_sq, "212 VIP Club")
    print("Guardado como:", os.path.abspath(outfile))

    plt.figure(figsize=(2.8, 2.8))
    plt.axis("off")
    plt.title("212 VIP Club", fontsize=10)
    plt.imshow(img_sq)
    plt.show()

if __name__ == "__main__":
    main()
