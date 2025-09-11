from flask import Flask, jsonify, request
from conexion.conexion import get_db_connection
import mysql.connector  # para capturar errores
from datetime import datetime  # <-- NUEVO: para generar email único

app = Flask(__name__)

# ---- Configuración MySQL ----
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flask'            # recomendado, no uses root
app.config['MYSQL_PASSWORD'] = 'Pipo.2009'    # tu clave
app.config['MYSQL_DATABASE'] = 'desarrollo_web'


@app.route('/')
def home():
    return '✅ Flask está corriendo. Prueba /test_db'


@app.route('/test_db')
def test_db():
    """Verifica la conexión y lista las tablas existentes."""
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tablas = [r[0] for r in cursor.fetchall()]
        return jsonify(tablas)
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de MySQL: {e.msg}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/agregar', methods=['GET'])
def agregar_demo():
    """Inserta un usuario con email único cada vez que accedes a /agregar."""
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        email = f"juan{int(datetime.now().timestamp())}@example.com"  # <-- único
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s,%s,%s)",
            ("Juan", email, "123456")
        )
        conn.commit()
        return jsonify({
            "mensaje": "Usuario agregado",
            "id_usuario": cursor.lastrowid,
            "email": email
        })
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de MySQL: {e.msg}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/agregar_json', methods=['POST'])
def agregar_json():
    """Inserta usando JSON: {nombre, email, password}."""
    data = request.get_json(force=True) or {}
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")
    if not all([nombre, email, password]):
        return jsonify({"error": "Faltan campos"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s,%s,%s)",
            (nombre, email, password)
        )
        conn.commit()
        return jsonify({"mensaje": "Usuario agregado", "id_usuario": cursor.lastrowid}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El email ya existe"}), 409
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de MySQL: {e.msg}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/eliminar/<int:id_usuario>', methods=['DELETE', 'GET'])
def eliminar(id_usuario):
    """Elimina por id. Acepta DELETE o GET (demo)."""
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        if cursor.rowcount:
            return jsonify({"mensaje": f"Usuario {id_usuario} eliminado"})
        return jsonify({"mensaje": "No encontrado"}), 404
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de MySQL: {e.msg}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/login', methods=['POST'])
def login():
    """Login simple: {email, password}."""
    data = request.get_json(force=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not all([email, password]):
        return jsonify({"error": "Faltan credenciales"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, nombre, email FROM usuarios WHERE email=%s AND password=%s",
            (email, password)
        )
        usuario = cursor.fetchone()
        if usuario:
            return jsonify({"mensaje": "Login exitoso", "usuario": usuario})
        return jsonify({"mensaje": "Credenciales incorrectas"}), 401
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de MySQL: {e.msg}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


if __name__ == '__main__':
    print("🚀 Iniciando Flask...")
    app.run(debug=True, host="127.0.0.1", port=5000)
