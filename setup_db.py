
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

cfg = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
}
db_name = os.getenv("MYSQL_DB", "flask_login_db")

conn = mysql.connector.connect(**cfg)
cur = conn.cursor()
cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
cur.execute(f"USE {db_name}")
cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(120) NULL,
  password VARCHAR(255) NOT NULL,
  rol ENUM('admin','user') DEFAULT 'user',
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()
cur.close()
conn.close()
print("DB initialized ✅")
