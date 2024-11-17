from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, numIdentificacion, Correo, Contraseña, Nombres="", Apellidos="", TipoDocumento="", FechaNacimiento="", Rol="") -> None:
        self.numIdentificacion = numIdentificacion
        self.Nombres = Nombres
        self.Apellidos = Apellidos
        self.TipoDocumento = TipoDocumento
        self.FechaNacimiento = FechaNacimiento
        self.Correo = Correo
        self.Contraseña = Contraseña
        self.Rol = Rol
        
    @classmethod
    def hashear_password(self, Contraseña):
        return generate_password_hash(Contraseña)
    
    @classmethod
    def check_password(self, hashed_password, Contraseña):
        return check_password_hash(hashed_password, Contraseña)
    
    