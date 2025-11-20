from dao.DatabaseConnection import DatabaseConnection

class AlumnosDAO:
    def obtener_alumnos():
        con = DatabaseConnection().get_connection()
        cursor = con.cursor(dictionary=True)
    
        cursor.execute("SELECT idAlumno, NombreCompleto FROM alumnos ORDER BY NombreCompleto ASC")
        registros = cursor.fetchall()
        cursor.close()
        return registros
