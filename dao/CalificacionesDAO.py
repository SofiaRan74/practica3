from DatabaseConnection import DatabaseConnection
import mysql.connector

class CalificacionesDAO:

    def listar_tbody(self):
        con = DatabaseConnection().get_connection()
        cursor = con.cursor(dictionary=True)

        sql = """
            SELECT c.idCalificacion, a.NombreCompleto, c.Calificacion, c.Categoria
            FROM calificaciones c
            INNER JOIN alumnos a ON c.idAlumno = a.idAlumno
            ORDER BY c.idCalificacion DESC
            LIMIT 10
        """

        cursor.execute(sql)
        registros = cursor.fetchall()
        cursor.close()
        return registros

    def buscar(self, busqueda="", id_filtro=None):
        con = DatabaseConnection().get_connection()
        cursor = con.cursor(dictionary=True)

        sql = """
            SELECT idCalificacion, idAlumno, NombreCompleto, Calificacion, Categoria
            FROM calificaciones
            INNER JOIN alumnos USING(idAlumno)
            WHERE 1=1
        """
        val = []

        if id_filtro:
            sql += " AND idCalificacion = %s "
            val.append(id_filtro)

        elif busqueda:
            busqueda = f"%{busqueda}%"
            sql += " AND (NombreCompleto LIKE %s OR Calificacion LIKE %s OR Categoria LIKE %s) "
            val.extend([busqueda, busqueda, busqueda])

        sql += " ORDER BY Calificacion DESC LIMIT 10"

        try:
            cursor.execute(sql, tuple(val))
            registros = cursor.fetchall()
        except mysql.connector.Error as error:
            print("SQL Error:", error)
            registros = []
        finally:
            cursor.close()

        return registros

    def guardar(self, idCalificacion, idAlumno, calificacion, categoria):
        con = DatabaseConnection().get_connection()
        cursor = con.cursor()

        if idCalificacion:
            sql = """
            UPDATE calificaciones
            SET idAlumno = %s,
                Calificacion = %s,
                Categoria = %s
            WHERE idCalificacion = %s
            """
            val = (idAlumno, calificacion, categoria, idCalificacion)
        else:
            sql = """
            INSERT INTO calificaciones (idAlumno, Calificacion, Categoria)
            VALUES (%s, %s, %s)
            """
            val = (idAlumno, calificacion, categoria)

        cursor.execute(sql, val)
        con.commit()
        cursor.close()
        return True

    def eliminar(self, idCalificacion):
        con = DatabaseConnection().get_connection()
        cursor = con.cursor()

        sql = "DELETE FROM calificaciones WHERE idCalificacion = %s"
        cursor.execute(sql, (idCalificacion,))
        con.commit()
        cursor.close()
        return True
