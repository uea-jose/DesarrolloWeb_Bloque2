from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, usuario, password, rol="user"):
        self.id = str(id)  # Flask-Login expects a str-like id
        self.usuario = usuario
        self.password = password
        self.rol = rol
