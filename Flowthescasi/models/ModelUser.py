from .entities.User import User


class ModelUser():

    @classmethod
    def login(self, mysql, user):
        try:
            cursor = mysql.connection.cursor()
            sql = """SELECT N°Identificacion, Nombres, Apellidos, TipoDocumento, FechaNacimiento, Correo, Contraseña FROM Usuario 
                    WHERE Correo = '{}'""".format(user.Correo)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0], row[1], row[2], row[3], row[4], row[5], User.check_password(row[6], user.Contraseña))
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, mysql, id):
        try:
            cursor = mysql.connection.cursor()
            sql = "SELECT id, username, fullname FROM user WHERE id = {}".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)