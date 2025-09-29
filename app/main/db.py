
# app/main/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "app" / "data" / "productos.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Garantiza el esquema final (3 tablas) y migra desde el esquema viejo si es necesario.
    """
    conn = get_conn(); cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=OFF;")

    # Si existe 'productos' pero sin 'categoria_id', migrar.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
    has_prod = cur.fetchone() is not None
    needs_migration = False
    if has_prod:
        cols = [r[1] for r in cur.execute("PRAGMA table_info(productos)").fetchall()]
        needs_migration = ("categoria_id" not in cols)

    if needs_migration:
        # Crear categorias si no existen y sembrar
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        """)
        cur.executemany("INSERT OR IGNORE INTO categorias(nombre) VALUES (?)",
                        [("Femenino",), ("Masculino",), ("Esencia",)])

        # Nueva tabla productos
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

        # Mapear tipo -> categoria_id
        def get_cat_id(tipo: str) -> int:
            t = (tipo or "").strip().lower()
            if t.startswith("f"): lookup = "Femenino"
            elif t.startswith("m"): lookup = "Masculino"
            else: lookup = "Esencia"
            r = cur.execute("SELECT id FROM categorias WHERE nombre=?", (lookup,)).fetchone()
            return int(r[0])

        rows = cur.execute("SELECT id, nombre, tipo, precio, stock FROM productos").fetchall()
        for r in rows:
            cat_id = get_cat_id(r[2])
            cur.execute(
                "INSERT INTO productos_new(id, nombre, descripcion, categoria_id, precio) VALUES (?,?,?,?,?)",
                (r[0], r[1], None, cat_id, r[3])
            )

        cur.execute("ALTER TABLE productos RENAME TO productos_old")
        cur.execute("ALTER TABLE productos_new RENAME TO productos")

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
                        (r[0], max(0, int(r[4] or 0))))

        cur.execute("DROP TABLE IF EXISTS productos_old")
        conn.commit()

    # Asegura esquema final (si estaba vacío)
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT,
        categoria_id INTEGER NOT NULL,
        precio REAL NOT NULL CHECK (precio>=0),
        FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER NOT NULL UNIQUE,
        stock INTEGER NOT NULL DEFAULT 0 CHECK (stock>=0),
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)
    cur.executemany("INSERT OR IGNORE INTO categorias(nombre) VALUES (?)",
                    [("Femenino",), ("Masculino",), ("Esencia",)])
    conn.commit()
    cur.execute("PRAGMA foreign_keys=ON;")
    conn.close()


def list_categorias():
    conn = get_conn()
    rows = conn.execute("SELECT id, nombre FROM categorias ORDER BY nombre").fetchall()
    conn.close()
    return rows

def upsert_producto(pid, nombre, descripcion, categoria_id, precio, stock):
    """Crea o actualiza producto y su inventario (stock)."""
    conn = get_conn(); cur = conn.cursor()
    if pid is None:
        cur.execute(
            "INSERT INTO productos(nombre, descripcion, categoria_id, precio) VALUES (?,?,?,?)",
            (nombre, descripcion, categoria_id, precio)
        )
        new_id = cur.lastrowid
        cur.execute("INSERT INTO inventario(producto_id, stock) VALUES (?,?)", (new_id, stock or 0))
        conn.commit(); conn.close()
        return new_id
    else:
        cur.execute(
            "UPDATE productos SET nombre=?, descripcion=?, categoria_id=?, precio=? WHERE id=?",
            (nombre, descripcion, categoria_id, precio, pid)
        )
        cur.execute(
            "INSERT INTO inventario(producto_id, stock) VALUES (?,?) ON CONFLICT(producto_id) DO UPDATE SET stock=excluded.stock",
            (pid, stock or 0)
        )
        conn.commit(); conn.close()
        return pid

def get_producto(pid):
    sql = """
    SELECT p.id, p.nombre, p.descripcion, p.categoria_id, c.nombre AS categoria,
           p.precio, COALESCE(i.stock,0) AS stock
      FROM productos p
      JOIN categorias c ON c.id=p.categoria_id
      LEFT JOIN inventario i ON i.producto_id=p.id
     WHERE p.id=?
    """
    conn = get_conn()
    row = conn.execute(sql, (pid,)).fetchone()
    conn.close()
    return row

def delete_producto(pid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=?", (pid,))
    conn.commit(); conn.close()

def search_productos(q=None, page=1, per_page=10):
    """Lista con paginación y búsqueda básica por nombre o categoría."""
    page = max(1, int(page or 1)); per_page = max(1, min(100, int(per_page or 10)))
    params = []
    where = ""
    if q:
        where = "WHERE lower(p.nombre) LIKE ? OR lower(c.nombre) LIKE ?"
        like = f"%{q.lower()}%"
        params.extend([like, like])
    base_sql = f"""
    FROM productos p
    JOIN categorias c ON c.id=p.categoria_id
    LEFT JOIN inventario i ON i.producto_id=p.id
    {where}
    """
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) " + base_sql, params).fetchone()[0]
    offset = (page-1)*per_page
    rows = conn.execute(
        "SELECT p.id, p.nombre, p.descripcion, c.nombre AS categoria, p.precio, COALESCE(i.stock,0) AS stock "
        + base_sql + " ORDER BY p.id DESC LIMIT ? OFFSET ?",
        (*params, per_page, offset)
    ).fetchall()
    conn.close()
    return rows, total

def nombre_existe(nombre, exclude_id=None):
    conn = get_conn(); cur = conn.cursor()
    if exclude_id is None:
        cur.execute("SELECT 1 FROM productos WHERE lower(nombre)=lower(?) LIMIT 1", (nombre,))
    else:
        cur.execute("SELECT 1 FROM productos WHERE lower(nombre)=lower(?) AND id<>? LIMIT 1", (nombre, exclude_id))
    r = cur.fetchone(); conn.close()
    return r is not None

def mysql_schema_sql():
    """Devuelve un script SQL compatible con MySQL 8 para crear las 3 tablas y datos base."""
    return """
-- schema_mysql.sql
CREATE TABLE IF NOT EXISTS categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL UNIQUE,
  descripcion TEXT NULL,
  categoria_id INT NOT NULL,
  precio DECIMAL(10,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_prod_cat FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS inventario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  producto_id INT NOT NULL UNIQUE,
  stock INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_inv_prod FOREIGN KEY (producto_id) REFERENCES productos(id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT IGNORE INTO categorias(nombre) VALUES ('Femenino'),('Masculino'),('Esencia');
"""
