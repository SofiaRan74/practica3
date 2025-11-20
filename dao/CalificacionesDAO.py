from .DatabaseConnection import DatabaseConnection
import mysql.connector

def obtener_tbody_calificaciones():
    con = DatabaseConnection().get_connection()
    cursor = con.cursor(dictionary=True)

    sql = """
        SELECT c.idCalificacion,
               a.NombreCompleto,
               c.Calificacion,
               c.Categoria
        FROM calificaciones c
        INNER JOIN alumnos a ON c.idAlumno = a.idAlumno
        ORDER BY c.idCalificacion DESC
        LIMIT 10
    """

    cursor.execute(sql)
    registros = cursor.fetchall()
    cursor.close()
    return registros

def buscar_calificaciones(busqueda="", id_filtro=None):
    con = DatabaseConnection().get_connection()
    cursor = con.cursor(dictionary=True)

    sql = """
        SELECT idCalificacion,
               idAlumno,
               NombreCompleto,
               Calificacion,
               Categoria
        FROM calificaciones
        INNER JOIN alumnos USING(idAlumno)
        WHERE 1=1
    """
    params = []

  
    if id_filtro:
        sql += " AND idCalificacion = %s "
        params.append(id_filtro)


    elif busqueda:
        b = f"%{busqueda}%"
        sql += " AND (NombreCompleto LIKE %s OR Calificacion LIKE %s OR Categoria LIKE %s) "
        params.extend([b, b, b])

    sql += " ORDER BY Calificacion DESC LIMIT 10"

    cursor.execute(sql, tuple(params))
    registros = cursor.fetchall()
    cursor.close()
    return registros


def obtener_alumnos():
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


def guardar_calificacion(idCalificacion, idAlumno, Calificacion, Categoria):
    con = DatabaseConnection().get_connection()
    cursor = con.cursor()

    # UPDATE
    if idCalificacion:
        sql = """
        UPDATE calificaciones
        SET idAlumno = %s,
            Calificacion = %s,
            Categoria = %s
        WHERE idCalificacion = %s
        """
        val = (idAlumno, Calificacion, Categoria, idCalificacion)

    else:
        sql = """
        INSERT INTO calificaciones (idAlumno, Calificacion, Categoria)
        VALUES (%s, %s, %s)
        """
        val = (idAlumno, Calificacion, Categoria)

    cursor.execute(sql, val)
    con.commit()
    cursor.close()
    return True


def eliminar_calificacion(idCalificacion):
    con = DatabaseConnection().get_connection()
    cursor = con.cursor()

    sql = "DELETE FROM calificaciones WHERE idCalificacion = %s"
    cursor.execute(sql, (idCalificacion,))

    con.commit()
    cursor.close()
    return True
