
import os
import mysql.connector
from mysql.connector import errorcode

def _env(name, default=None, cast=str):
    val = os.environ.get(name, default)
    if val is None:
        return None
    try:
        return cast(val) if cast and val is not None else val
    except Exception:
        return val

def ensure_database_and_tables(logger=None):
    """Ensure DB and required tables exist. Safe to run multiple times."""
    host = _env("MYSQL_HOST", "127.0.0.1")
    port = _env("MYSQL_PORT", 3306, int)
    user = _env("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    dbname = _env("MYSQL_DB", "flask_login_db")

    def log(msg):
        if logger:
            try:
                logger.info(msg)
            except Exception:
                print(msg)
        else:
            print(msg)

    # Connect without database to create the DB if needed
    try:
        conn = mysql.connector.connect(host=host, port=port, user=user, password=password)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cur.close()
        conn.close()
        log(f"[db_init] Database ensured: {dbname}")
    except mysql.connector.Error as err:
        log(f"[db_init] Error ensuring database: {err}")
        return False

    # Now connect to the database and ensure tables
    try:
        conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=dbname)
        conn.autocommit = True
        cur = conn.cursor()
        # users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(120) NULL,
                password VARCHAR(255) NOT NULL,
                rol ENUM('admin','user') DEFAULT 'user',
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)
        cur.close()
        conn.close()
        log("[db_init] Tables ensured.")
        return True
    except mysql.connector.Error as err:
        log(f"[db_init] Error ensuring tables: {err}")
        return False
