# Proyecto: Login con Flask + MySQL (mysql-connector)

## Requisitos
- Python 3.10+
- MySQL/MariaDB en local (XAMPP OK)
- `pip install -r requirements.txt`

## Configuración rápida
1. Copia `.env.example` a `.env` y ajusta si hace falta (por defecto usa `flag_user` / `FlagUserPass!234` y DB `flask_login_db`).
2. Inicializa entorno e instala dependencias:
   ```bash
   python -m venv .venv
   . .venv/Scripts/activate    # Windows
   pip install -r requirements.txt
   ```
3. Asegúrate de que el usuario DB tiene permisos sobre la base (si no, usa SQL del final).
4. (Opcional) inicializa la DB:
   ```bash
   python setup_db.py
   ```

## Ejecutar
```bash
python run.py
# abre http://127.0.0.1:5000/login
```

## Esquema de la DB
```sql
CREATE DATABASE IF NOT EXISTS flask_login_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE flask_login_db;

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(120) NULL,
  password VARCHAR(255) NOT NULL,
  rol ENUM('admin','user') DEFAULT 'user',
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Permisos recomendados (ejecutar como root)
```sql
CREATE USER IF NOT EXISTS 'flag_user'@'localhost' IDENTIFIED BY 'FlagUserPass!234';
GRANT ALL PRIVILEGES ON flask_login_db.* TO 'flag_user'@'localhost';
FLUSH PRIVILEGES;
```


## Arranque sin `setup_db.py` (Auto-init)
Desde esta versión, la base de datos y la tabla `usuarios` se crean automáticamente al iniciar la app,
usando los valores de entorno (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`).
Esto ocurre dentro de `app/__init__.py` llamando a `ensure_database_and_tables()` de `app/db_init.py`.
Es seguro en ejecuciones concurrentes y no es necesario correr scripts adicionales en Render.
