
from flask import current_app
from mysql.connector import pooling

_pool = None

def _get_pool():
    global _pool
    if _pool is None:
        cfg = current_app.config
        conn_args = {
            "host": cfg.get("MYSQL_HOST", "127.0.0.1"),
            "port": int(cfg.get("MYSQL_PORT", 3306)),
            "user": cfg.get("MYSQL_USER", "root"),
            "password": cfg.get("MYSQL_PASSWORD", ""),
            "database": cfg.get("MYSQL_DB", "flask_login_db"),
        }
        auth_plugin = cfg.get("MYSQL_AUTH_PLUGIN")
        if auth_plugin:
            conn_args["auth_plugin"] = auth_plugin

        _pool = pooling.MySQLConnectionPool(
            pool_name="flask_pool",
            pool_size=int(cfg.get("MYSQL_POOL_SIZE", 5)),
            **conn_args,
        )
    return _pool

def get_conn():
    return _get_pool().get_connection()

def get_user_by_usuario(usuario: str):
    cnx = get_conn()
    try:
        cur = cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id, usuario, email, password, rol FROM usuarios WHERE usuario=%s",
            (usuario,),
        )
        return cur.fetchone()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        cnx.close()

def get_user_by_id(user_id: str):
    cnx = get_conn()
    try:
        cur = cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id, usuario, email, password, rol FROM usuarios WHERE id=%s",
            (user_id,),
        )
        return cur.fetchone()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        cnx.close()

def insert_user(usuario: str, email: str, password_hash: str) -> int:
    cnx = get_conn()
    try:
        cur = cnx.cursor()
        cur.execute(
            "INSERT INTO usuarios (usuario, email, password) VALUES (%s, %s, %s)",
            (usuario, email, password_hash),
        )
        cnx.commit()
        return cur.lastrowid
    finally:
        try:
            cur.close()
        except Exception:
            pass
        cnx.close()
