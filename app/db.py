import os
import mysql.connector
from werkzeug.security import generate_password_hash

MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DB', 'desarrollo_web')

def _server_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        autocommit=True
    )

def get_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DB, autocommit=True
    )

def init_db():
    # Crea base de datos si no existe
    srv = _server_conn()
    cur = srv.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.close(); srv.close()

    # Crea tabla usuarios y seed
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        rol ENUM('admin','cliente','visor') NOT NULL DEFAULT 'cliente',
        activo TINYINT(1) NOT NULL DEFAULT 1,
        creado_en TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ''')

    # seed admin/admin
    cur2 = conn.cursor(dictionary=True)
    cur2.execute("SELECT 1 FROM usuarios WHERE usuario='admin' LIMIT 1")
    if not cur2.fetchone():
        cur.execute(
            "INSERT INTO usuarios (usuario, password, rol, activo) VALUES (%s,%s,%s,%s)",
            ('admin', generate_password_hash('admin'), 'admin', 1)
        )
    conn.commit()
    cur2.close(); cur.close(); conn.close()

def get_user_by_id(user_id: str):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, usuario, password, rol, activo FROM usuarios WHERE id=%s", (user_id,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row

def get_user_by_usuario(usuario: str):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, usuario, password, rol, activo FROM usuarios WHERE usuario=%s", (usuario,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row

def insert_user(usuario: str, password_hash: str, rol: str='cliente', activo: int=1):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (usuario, password, rol, activo) VALUES (%s,%s,%s,%s)",
                (usuario, password_hash, rol, activo))
    conn.commit(); cur.close(); conn.close()


# ===== Categorías =====
def listar_categorias():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
    data = cur.fetchall(); cur.close(); conn.close(); return data


# ===== Productos & Inventario =====
def listar_productos():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT p.id, p.nombre, p.descripcion,
               c.nombre AS categoria,
               i.sku, i.stock, i.precio
        FROM productos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        LEFT JOIN inventario i ON i.producto_id = p.id
        ORDER BY p.id DESC
        """
    )
    data = cur.fetchall(); cur.close(); conn.close(); return data

def obtener_producto(prod_id):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT p.id, p.nombre, p.descripcion, p.categoria_id,
               i.sku, i.stock, i.precio
        FROM productos p
        LEFT JOIN inventario i ON i.producto_id = p.id
        WHERE p.id=%s
        """, (prod_id,)
    )
    data = cur.fetchone(); cur.close(); conn.close(); return data

def crear_producto(nombre, descripcion, categoria_id, sku, stock, precio):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO productos(nombre, descripcion, categoria_id) VALUES (%s,%s,%s)", (nombre, descripcion, categoria_id))
    prod_id = cur.lastrowid
    cur.execute("INSERT INTO inventario(producto_id, sku, stock, precio) VALUES (%s,%s,%s,%s)", (prod_id, sku, stock, precio))
    conn.commit(); cur.close(); conn.close(); return prod_id

def actualizar_producto(prod_id, nombre, descripcion, categoria_id, sku, stock, precio):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE productos SET nombre=%s, descripcion=%s, categoria_id=%s WHERE id=%s", (nombre, descripcion, categoria_id, prod_id))
    cur.execute("SELECT id FROM inventario WHERE producto_id=%s", (prod_id,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE inventario SET sku=%s, stock=%s, precio=%s WHERE producto_id=%s", (sku, stock, precio, prod_id))
    else:
        cur.execute("INSERT INTO inventario(producto_id, sku, stock, precio) VALUES (%s,%s,%s,%s)", (prod_id, sku, stock, precio))
    conn.commit(); cur.close(); conn.close()

def eliminar_producto(prod_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=%s", (prod_id,))
    conn.commit(); cur.close(); conn.close()


def _ensure_crud_tables():
    conn = get_conn(); cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS categoria (
      id INT AUTO_INCREMENT PRIMARY KEY,
      nombre VARCHAR(50) NOT NULL,
      slug   VARCHAR(50) NOT NULL,
      creado_en TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE KEY uq_categoria_nombre (nombre),
      UNIQUE KEY uq_categoria_slug   (slug)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS productos (
      id INT AUTO_INCREMENT PRIMARY KEY,
      codigo VARCHAR(10) NULL,
      nombre VARCHAR(255) NOT NULL,
      categoria_id INT NOT NULL,
      descripcion TEXT NULL,
      precio DECIMAL(10,2) NOT NULL DEFAULT 0.00,
      stock INT NOT NULL DEFAULT 0,
      creado_en TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
      actualizado_en TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      UNIQUE KEY uq_nombre (nombre),
      KEY ix_categoria (categoria_id),
      CONSTRAINT fk_productos_categoria
        FOREIGN KEY (categoria_id) REFERENCES categoria(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ''')
    cur.execute("INSERT IGNORE INTO categoria (id,nombre,slug) VALUES (1,'Femenino','femenino'),(2,'Masculino','masculino'),(3,'Esencia','esencia')")
    conn.commit(); cur.close(); conn.close()

try:
    _ensure_crud_tables()
except Exception:
    pass


# === CRUD Productos (corregido) ===
def listar_categorias():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nombre FROM categoria ORDER BY nombre ASC")
    rows = cur.fetchall(); cur.close(); conn.close(); return rows

def listar_productos():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute('''
        SELECT p.id, p.codigo, p.nombre, p.descripcion, p.precio, p.stock,
               c.nombre AS categoria
        FROM productos p
        JOIN categoria c ON c.id = p.categoria_id
        ORDER BY p.nombre ASC
    ''')
    rows = cur.fetchall(); cur.close(); conn.close(); return rows

def obtener_producto(pid: int):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute('''
        SELECT p.id, p.codigo, p.nombre, p.descripcion, p.precio, p.stock, p.categoria_id
        FROM productos p WHERE p.id=%s
    ''', (pid,))
    row = cur.fetchone(); cur.close(); conn.close(); return row

def crear_producto(nombre, descripcion, categoria_id, precio, stock):
    conn = get_conn(); cur = conn.cursor()
    cur.execute('''
        INSERT INTO productos (nombre, descripcion, categoria_id, precio, stock)
        VALUES (%s,%s,%s,%s,%s)
    ''', (nombre, descripcion, categoria_id, precio, stock))
    conn.commit(); cur.close(); conn.close()

def actualizar_producto(pid, nombre, descripcion, categoria_id, precio, stock):
    conn = get_conn(); cur = conn.cursor()
    cur.execute('''
        UPDATE productos
        SET nombre=%s, descripcion=%s, categoria_id=%s, precio=%s, stock=%s
        WHERE id=%s
    ''', (nombre, descripcion, categoria_id, precio, stock, pid))
    conn.commit(); cur.close(); conn.close()

def eliminar_producto(pid: int):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=%s", (pid,))
    conn.commit(); cur.close(); conn.close()


# --- Paginación de productos ---
def contar_productos():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM productos")
    total = cur.fetchone()[0]
    cur.close(); conn.close(); return total

def listar_productos_paginado(limit: int, offset: int):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.id, p.codigo, p.nombre, p.descripcion, p.precio, p.stock,
               c.nombre AS categoria
        FROM productos p
        JOIN categoria c ON c.id = p.categoria_id
        ORDER BY p.nombre ASC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def contar_productos_categoria(slug: str):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM productos p
        JOIN categoria c ON c.id = p.categoria_id
        WHERE c.slug = %s
    """, (slug,))
    total = cur.fetchone()[0]
    cur.close(); conn.close(); return total

def listar_productos_categoria_paginado(slug: str, limit: int, offset: int):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.id, p.codigo, p.nombre, p.descripcion, p.precio, p.stock,
               c.nombre AS categoria, c.slug AS categoria_slug
        FROM productos p
        JOIN categoria c ON c.id = p.categoria_id
        WHERE c.slug = %s
        ORDER BY p.nombre ASC
        LIMIT %s OFFSET %s
    """, (slug, limit, offset))
    rows = cur.fetchall()
    cur.close(); conn.close(); return rows

def obtener_productos_por_ids(id_list):
    if not id_list:
        return []
    placeholders = ','.join(['%s'] * len(id_list))
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute(f"""
        SELECT p.id, p.nombre, p.precio
        FROM productos p
        WHERE p.id IN ({placeholders})
    """, tuple(id_list))
    rows = cur.fetchall()
    cur.close(); conn.close(); return rows
