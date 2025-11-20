from flask import session
from datetime import datetime
import pytz
from DatabaseConnection import DatabaseConnection

class UsuariosDAO:

    def iniciar_sesion(self, usuario, contrasena):
        con = DatabaseConnection().get_connection()
        cursor = con.cursor(dictionary=True)

        sql = """
            SELECT Id_Usuario, Nombre_Usuario, Tipo_Usuario
            FROM usuarios
            WHERE Nombre_Usuario = %s
            AND Contrasena = %s
        """
        cursor.execute(sql, (usuario, contrasena))
        registros = cursor.fetchall()
        cursor.close()
        return registros

    def guardar_log_sesion(self, usuario, accion):
        tz = pytz.timezone("America/Matamoros")
        fechaHora = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        with open("log-sesiones.txt", "a") as f:
            f.write(f"{usuario}\t{accion}\t{fechaHora}\n")

