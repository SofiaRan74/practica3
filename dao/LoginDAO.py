from dao.DatabaseConnection import DatabaseConnection

class LoginDAO:

    def __init__(self):
        self.db = DatabaseConnection()

    def validar_credenciales(self, usuario, password):
        con = self.db.get_connection()
        cursor = con.cursor(dictionary=True)

        sql = """
            SELECT * FROM usuarios 
            WHERE usuario = %s AND password = %s
        """

        cursor.execute(sql, (usuario, password))
        data = cursor.fetchone()

        cursor.close()
        con.close()
        return data is not None
