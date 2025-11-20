from DatabaseConnection import DatabaseConnection

class AlumnosDAO:

    def listar(self):
        con = DatabaseConnection().get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute("""
            SELECT idAlumno, NombreCompleto
            FROM alumnos
            ORDER BY NombreCompleto ASC
        """)
        registros = cursor.fetchall()
        cursor.close()
        return registros
