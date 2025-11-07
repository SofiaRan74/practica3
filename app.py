from flask import Flask, render_template, request, jsonify, make_response, session
import mysql.connector
import mysql.connector.pooling
import pusher
import datetime
import pytz
from flask_cors import CORS, cross_origin
from functools import wraps  # 👈 Necesario para el decorador

app = Flask(__name__)
app.secret_key = "Test12345"
CORS(app)

# ---------- CONEXIÓN A BASE DE DATOS ----------
con_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    host="185.232.14.52",
    database="u760464709_23005116_bd",
    user="u760464709_23005116_usr",
    password="z8[T&05u"
)

# ---------- PUSHER ----------
def pusherApoyos():
    pusher_client = pusher.Pusher(
        app_id='1891402',
        key='505a9219e50795c4885e',
        secret='fac4833b05652932a8bc',
        cluster='us2',
        ssl=True
    )

    pusher_client.trigger("for-nature-533", "eventoCalificaciones", {"message": "Hola Mundo!"})
    return make_response(jsonify({}))

# ---------- DECORADOR DE LOGIN ----------
def requiere_login(fun):
    @wraps(fun)
    def decorador(*args, **kwargs):
        if not session.get("login"):
            return jsonify({"error": "No has iniciado sesión"}), 401
        return fun(*args, **kwargs)
    return decorador

# ---------- RUTAS ----------
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

    con = con_pool.get_connection()
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
    con.close()

    session["login"] = False
    session["login-usr"] = None
    session["login-tipo"] = 0

    if registros:
        usuario = registros[0]
        session["login"] = True
        session["login-usr"] = usuario["Nombre_Usuario"]
        session["login-tipo"] = usuario["Tipo_Usuario"]

    return make_response(jsonify(registros))


@app.route("/cerrarSesion", methods=["POST"])
@requiere_login
def cerrarSesion():
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
    return render_template("calificaciones.html")


@app.route("/tbodyCalificacion")
def tbodyCalificacion():
    con = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
        SELECT idCalificacion,
               idAlumno,
               Calificacion,
               Categoria
        FROM calificaciones
        ORDER BY idCalificacion DESC
        LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template("tbodyCalificacion.html", apoyos=registros)


@app.route("/calificaciones/buscar", methods=["GET"])
def buscarCalificaciones():
    con = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)

    args = request.args
    busqueda = args.get("busqueda", "")
    busqueda = f"%{busqueda}%"

    sql = """
        SELECT idCalificacion,
               idAlumno,
               Calificacion,
               Categoria
        FROM calificaciones
        WHERE idAlumno LIKE %s
        OR Calificacion LIKE %s
        OR Categoria LIKE %s
        ORDER BY idCalificacion DESC
        LIMIT 10 OFFSET 0
    """
    val = (busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []
    finally:
        cursor.close()
        con.close()

    return make_response(jsonify(registros))


@app.route("/fechaHora")
def fechaHora():
    zona = pytz.timezone("America/Mexico_City")
    ahora = datetime.datetime.now(zona)
    return ahora.strftime("%Y-%m-%d %H:%M:%S")


# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    app.run(debug=True)
