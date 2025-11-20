from flask import Flask, render_template, request, jsonify, make_response, session, send_from_directory
from functools import wraps
import datetime
import pytz
import pusher
from flask_cors import CORS

# DAOs
from dao.UsuariosDAO import UsuariosDAO
from dao.AlumnosDAO import AlumnosDAO
from dao.CalificacionesDAO import CalificacionesDAO

# Singleton DB (original)
from dao.DatabaseConnection import DatabaseConnection

app = Flask(__name__)
app.secret_key = "Test12345"
CORS(app)

usuariosDAO = UsuariosDAO()
alumnosDAO = AlumnosDAO()
calificacionesDAO = CalificacionesDAO()


def pusherCalificaciones():
    pusher_client = pusher.Pusher(
        app_id='1891402',
        key='505a9219e50795c4885e',
        secret='fac4833b05652932a8bc',
        cluster='us2',
        ssl=True
    )
    pusher_client.trigger("for-nature-533", "eventoCalificaciones", {"message": "Actualizado"})


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

    registros = usuariosDAO.iniciar_sesion(usuario, contrasena)

    if registros:
        info = registros[0]
        session["login"] = True
        session["login-usr"] = info["Nombre_Usuario"]
        session["login-tipo"] = info["Tipo_Usuario"]
        usuariosDAO.guardar_log_sesion(info["Nombre_Usuario"], "Inicio de sesión")
    else:
        usuariosDAO.guardar_log_sesion(usuario, "Intento fallido")

    return jsonify(registros)


@app.route("/cerrarSesion", methods=["POST"])
@requiere_login
def cerrarSesion():
    usr = session.get("login-usr", "Desconocido")
    usuariosDAO.guardar_log_sesion(usr, "Cierre de sesión")

    session.clear()
    return jsonify({})


@app.route("/preferencias")
@requiere_login
def preferencias():
    return jsonify({
        "usr": session.get("login-usr"),
        "tipo": session.get("login-tipo", 2)
    })


@app.route("/calificaciones")
def calificaciones():
    return send_from_directory("templates", "calificaciones.html")


@app.route("/datos")
def datos():
    return send_from_directory("templates", "datos.html")


# --------------------------
# RUTAS LLAMANDO A LOS DAOs
# --------------------------

@app.route("/alumnos", methods=["GET"])
def getAlumnos():
    return jsonify(alumnosDAO.listar())


@app.route("/tbodyCalificacion")
def tbodyCalificacion():
    registros = calificacionesDAO.listar_tbody()
    return render_template("tbodyCalificacion.html", calificaciones=registros)


@app.route("/calificaciones/buscar", methods=["GET"])
def buscarCalificaciones():
    bus = request.args.get("busqueda", "")
    id_f = request.args.get("id")
    registros = calificacionesDAO.buscar(busqueda=bus, id_filtro=id_f)
    return jsonify(registros)


@app.route("/calificacion", methods=["POST"])
def guardarCalificacion():
    idCal = request.form["idCalificacion"]
    idAl = request.form["idAlumno"]
    cal = request.form["calificacion"]
    cat = request.form["categoria"]

    calificacionesDAO.guardar(idCal, idAl, cal, cat)
    pusherCalificaciones()
    return jsonify({})


@app.route("/calificacion/eliminar", methods=["POST"])
def eliminarCalificacion():
    idCal = request.form["idCalificacion"]
    calificacionesDAO.eliminar(idCal)
    return jsonify({})


@app.route("/fechaHora")
def fechaHora():
    tz = pytz.timezone("America/Mexico_City")
    return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    app.run(debug=True)
