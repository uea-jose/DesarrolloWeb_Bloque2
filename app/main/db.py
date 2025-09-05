# app/main/db.py
import sqlite3
from pathlib import Path

# Ruta a la BD (manteniendo tu estilo actual)
DB_PATH = Path(__file__).resolve().parents[2] / "app" / "data" / "productos.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
#  Esquema mínimo
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo   TEXT NOT NULL,                  -- 'Femenino' | 'Masculino' | 'Unisex' (soportado 'F'/'M' también)
            precio REAL NOT NULL CHECK(precio>=0),
            stock  INTEGER NOT NULL DEFAULT 0 CHECK(stock>=0)
        )
    """)
    conn.commit()
    conn.close()

# =========================
#  QUERIES para catálogo/carrito
# =========================
def fetch_products_by_gender(gender: str):
    """
    Devuelve perfumes por género, aceptando valores como:
      - 'F', 'Femenino', 'femenina', 'female'
      - 'M', 'Masculino', 'masculina', 'male'
    Estructura de salida: slug, name, brand(None), gender('F'|'M'), price, stock, image_url(None), color(None)
    """
    g = (gender or "").strip().lower()
    is_f = g.startswith("f")  # f, femenino, femenina, female
    is_m = g.startswith("m")  # m, masculino, masculina, male

    if is_f:
        where = "lower(tipo) IN ('f','femenino','femenina','female')"
        gender_case = "'F'"
    elif is_m:
        where = "lower(tipo) IN ('m','masculino','masculina','male')"
        gender_case = "'M'"
    else:
        # si envían cualquier otra cosa, no devolvemos nada
        where = "1=0"
        gender_case = "upper(substr(tipo,1,1))"

    sql = f"""
    SELECT
        lower(replace(nombre,' ','-')) AS slug,
        nombre                         AS name,
        NULL                           AS brand,
        CASE WHEN lower(tipo) IN ('f','femenino','femenina','female') THEN 'F'
             WHEN lower(tipo) IN ('m','masculino','masculina','male') THEN 'M'
             ELSE {gender_case}
        END                            AS gender,
        precio                         AS price,
        stock                          AS stock,
        NULL                           AS image_url,
        NULL                           AS color
    FROM productos
    WHERE {where}
    ORDER BY nombre
    """
    conn = get_conn()
    rows = conn.execute(sql).fetchall()
    conn.close()
    return rows

def apply_stock(slug: str, delta: int):
    """
    Aplica un cambio de stock para el producto identificado por el *slug virtual*
    (lower(replace(nombre,' ','-'))).
      - delta > 0  -> reservar (resta stock) **sólo si hay stock suficiente**
      - delta < 0  -> devolver (suma stock)
    Retorna: (ok: bool, new_stock: int)

    Si no hay stock suficiente en una reserva (delta>0), ok=False y new_stock=stock actual.
    """
    conn = get_conn()
    cur = conn.cursor()

    if delta > 0:
        # Reserva: resta si hay stock suficiente
        cur.execute(
            """
            UPDATE productos
               SET stock = stock - ?
             WHERE lower(replace(nombre,' ','-')) = ?
               AND stock >= ?
            """,
            (delta, slug, delta),
        )
        if cur.rowcount == 0:
            # No alcanzó el stock: devolvemos el stock actual
            row = conn.execute(
                "SELECT stock FROM productos WHERE lower(replace(nombre,' ','-')) = ?",
                (slug,),
            ).fetchone()
            conn.close()
            return False, (row["stock"] if row else 0)
        conn.commit()
    else:
        # Devolución: delta es negativo -> restarle un negativo = sumar stock
        cur.execute(
            """
            UPDATE productos
               SET stock = stock - ?
             WHERE lower(replace(nombre,' ','-')) = ?
            """,
            (delta, slug),
        )
        conn.commit()

    # Stock actualizado
    row = conn.execute(
        "SELECT stock FROM productos WHERE lower(replace(nombre,' ','-')) = ?",
        (slug,),
    ).fetchone()
    conn.close()
    return True, (row["stock"] if row else 0)


# ==== Unicidad por nombre (case-insensitive) ====
def ensure_unique_index():
    """
    Crea un índice único case-insensitive sobre lower(nombre).
    No falla si ya existe.
    """
    conn = get_conn(); cur = conn.cursor()
    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_productos_nombre_ci "
        "ON productos(lower(nombre))"
    )
    conn.commit(); conn.close()

def nombre_existe(nombre: str, exclude_id: int | None = None) -> bool:
    """
    Devuelve True si existe un producto con ese nombre (case-insensitive).
    exclude_id: opcional para permitir editar el mismo registro.
    """
    conn = get_conn(); cur = conn.cursor()
    if exclude_id is None:
        cur.execute("SELECT 1 FROM productos WHERE lower(nombre)=lower(?) LIMIT 1", (nombre,))
    else:
        cur.execute(
            "SELECT 1 FROM productos WHERE lower(nombre)=lower(?) AND id<>? LIMIT 1",
            (nombre, exclude_id),
        )
    row = cur.fetchone()
    conn.close()
    return row is not None
