import mysql.connector
from flask import current_app

def get_db_connection():
    """
    Devuelve una conexión a MySQL usando la configuración del app.
    Maneja errores de conexión y los levanta para Flask.
    """
    try:
        conn = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DATABASE'],
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        raise
