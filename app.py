from flask import Flask, render_template, request, jsonify, make_response, session, send_from_directory
import mysql.connector
import pusher
import datetime
import pytz
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
app.secret_key = "Test12345"
CORS(app)


class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self._connection = mysql.connector.connect(
                host="185.232.14.52",
                database="u760464709_23005116_bd",
                user="u760464709_23005116_usr",
                password="z8[T&05u"
            )
            print("✅ Conexión Singleton MySQL establecida")
        except mysql.connector.Error as err:
            print(f"❌ Error al conectar con MySQL: {err}")

    def get_connection(self):
        # Reabrir si se cayó
        if not self._connection.is_connected():
            self._connect()
        return self._connection

def pusherCalificaciones():
    pusher_client = pusher.Pusher(
        app_id='1891402',
        key='505a9219e50795c4885e',
        secret='fac4833b05652932a8bc',
        cluster='us2',
        ssl=True
    )

    pusher_client.trigger("for-nature-533", "eventoCalificaciones", {"message": "Hola Mundo!"})
    return make_response(jsonify({}))


def requiere_login(fun):
    @wraps(fun)
    def decorador(*args, **kwargs):
        if not session.get("login"):
            return jsonify({"error": "No has iniciado sesión"}), 401
        return fun(*args, **kwargs)
    return decorador
    

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/iniciarSesion", methods=["POST"])
def iniciarSesion():
    usuario = request.form["usuario"]
    contrasena = request.form["contrasena"]

    con = DatabaseConnection().get_connection()
    cursor = con.cursor(dictionary=True)

    sql = """
        SELECT Id_Usuario, Nombre_Usuario, Tipo_Usuario
        FROM usuarios
        WHERE Nombre_Usuario = %s
        AND Contrasena = %s
    """
    val = (usuario, contrasena)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    cursor.close()

    if registros:
        usuario_info = registros[0]
        session["login"] = True
        session["login-usr"] = usuario_info["Nombre_Usuario"]
        session["login-tipo"] = usuario_info["Tipo_Usuario"]
        registrar_log_sesion(usuario_info["Nombre_Usuario"], "Inicio de sesión")
    else:
        registrar_log_sesion(usuario, "Intento fallido")

    return make_response(jsonify(registros))


def registrar_log_sesion(usuario, accion):
    tz = pytz.timezone("America/Matamoros")
    ahora = datetime.datetime.now(tz)
    fechaHoraStr = ahora.strftime("%Y-%m-%d %H:%M:%S")

    with open("log-sesiones.txt", "a") as f:
        f.write(f"{usuario}\t{accion}\t{fechaHoraStr}\n")


@app.route("/cerrarSesion", methods=["POST"])
@requiere_login
def cerrarSesion():
    usuario = session.get("login-usr", "Desconocido")
    registrar_log_sesion(usuario, "Cierre de sesión")

    session["login"] = False
    session["login-usr"] = None
    session["login-tipo"] = 0
    return make_response(jsonify({}))


@app.route("/preferencias")
@requiere_login
def preferencias():
    return make_response(jsonify({
        "usr": session.get("login-usr"),
        "tipo": session.get("login-tipo", 2)
    }))


@app.route("/calificaciones")
def calificaciones():
    return send_from_directory("templates", "calificaciones.html")


@app.route("/tbodyCalificacion")
def tbodyCalificacion():
    con = DatabaseConnection().get_connection()
    cursor = con.cursor(dictionary=True)

    sql = """
        SELECT idCalificacion, idAlumno, Calificacion, Categoria
        FROM calificaciones
        ORDER BY idCalificacion DESC
        LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()
    cursor.close()

    return render_template("tbodyCalificacion.html", calificaciones=registros)


@app.route("/calificaciones/buscar", methods=["GET"])
def buscarCalificaciones():
    con = DatabaseConnection().get_connection()
    cursor = con.cursor(dictionary=True)

    busqueda = request.args.get("busqueda", "")
    busqueda = f"%{busqueda}%"

    sql = """
        SELECT idCalificacion,
               NombreCompleto,
               Calificacion,
               Categoria
        FROM calificaciones
        INNER JOIN alumnos USING(idAlumno)
        WHERE idAlumno LIKE %s
        OR Calificacion LIKE %s
        OR Categoria LIKE %s
        ORDER BY Calificacion DESC
        LIMIT 10 OFFSET 0
    """
    val = (busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error en MySQL: {error}")
        registros = []
    finally:
        cursor.close()

    return make_response(jsonify(registros))

@app.route("/calificacion", methods=["POST"])
def guardarCalificacion():
    con = DatabaseConnection().get_connection()
    cursor = con.cursor()

    idCalificacion = request.form["idCalificacion"]
    idAlumno = request.form["idAlumno"]
    Calificacion = request.form["calificacion"]
    Categoria = request.form["categoria"]

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

    pusherCalificaciones()

    return make_response(jsonify({}))

@app.route("/calificacion/eliminar", methods=["POST"])
def eliminarCalificacion():
    con = DatabaseConnection().get_connection()

    idCalificacion = request.form["idCalificacion"]

    cursor = con.cursor()
    sql = """
    DELETE FROM calificaciones
    WHERE idCalificacion = %s
    """
    val = (idCalificacion,)

    cursor.execute(sql, val)
    con.commit()
    cursor.close()

    return make_response(jsonify({}))

@app.route("/fechaHora")
def fechaHora():
    zona = pytz.timezone("America/Mexico_City")
    ahora = datetime.datetime.now(zona)
    return ahora.strftime("%Y-%m-%d %H:%M:%S")


@app.route("/log", methods=["GET"])
def logProductos():
    actividad = request.args["actividad"]
    descripcion = request.args["descripcion"]

    tz = pytz.timezone("America/Matamoros")
    fechaHoraStr = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    with open("log-busquedas.txt", "a") as f:
        f.write(f"{actividad}\t{descripcion}\t{fechaHoraStr}\n")

    with open("log-busquedas.txt") as f:
        log = f.read()

    return log


if __name__ == "__main__":
    app.run(debug=True)

