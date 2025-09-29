
"""
Migración de SQLite para pasar del esquema antiguo:
productos(id, nombre, tipo, precio, stock)
al nuevo esquema de 3 tablas: categorias, productos, inventario.

Ejecuta:
  python scripts/migrar_sqlite.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "productos.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys=OFF;")

# Detectar si ya existe el nuevo esquema
cols = [r[1] for r in cur.execute("PRAGMA table_info(productos)").fetchall()]
if "categoria_id" in cols:
    print("La columna categoria_id ya existe. No se requiere migración.")
    conn.close()
    raise SystemExit(0)

print("==> Iniciando migración...")

# 1) Crear tabla categorias y sembrar datos
cur.execute("""
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)""")
for nombre in ("Femenino","Masculino","Esencia"):
    cur.execute("INSERT OR IGNORE INTO categorias(nombre) VALUES (?)", (nombre,))

# 2) Crear nueva tabla productos con el esquema correcto
cur.execute("""
CREATE TABLE productos_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    categoria_id INTEGER NOT NULL,
    precio REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
)
""")

# 3) Migrar registros desde productos antiguo -> productos_new
#    Mapear "tipo" a categoria_id
def get_cat_id(tipo: str) -> int:
    t = (tipo or "").strip().lower()
    if t.startswith("f"): lookup = "Femenino"
    elif t.startswith("m"): lookup = "Masculino"
    else: lookup = "Esencia"
    r = cur.execute("SELECT id FROM categorias WHERE nombre=?", (lookup,)).fetchone()
    return int(r["id"])

rows = cur.execute("SELECT id, nombre, tipo, precio, stock FROM productos").fetchall()
for r in rows:
    cat_id = get_cat_id(r["tipo"])
    cur.execute("INSERT INTO productos_new(id, nombre, descripcion, categoria_id, precio) VALUES (?,?,?,?,?)",
                (r["id"], r["nombre"], None, cat_id, r["precio"]))

# 4) Renombrar tablas: productos_old y productos_new -> productos
cur.execute("ALTER TABLE productos RENAME TO productos_old")
cur.execute("ALTER TABLE productos_new RENAME TO productos")

# 5) Crear tabla inventario y volcar stock
cur.execute("""
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL UNIQUE,
    stock INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
)
""")
for r in rows:
    cur.execute("INSERT OR IGNORE INTO inventario(producto_id, stock) VALUES (?,?)",
                (r["id"], max(0, int(r["stock"] or 0))))

# 6) Eliminar tabla antigua
cur.execute("DROP TABLE IF EXISTS productos_old")

conn.commit()
conn.execute("PRAGMA foreign_keys=ON;")
conn.close()
print("==> Migración completada correctamente.")
