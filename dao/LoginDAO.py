def login_usuario(usuario, contrasena):
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
