from flask import Flask, jsonify, request, render_template
from dao.AlumnosDAO import AlumnosDAO
from dao.CalificacionesDAO import CalificacionesDAO
from dao.LoginDAO import LoginDAO

app = Flask(__name__)

alumnos_dao = AlumnosDAO()
calificaciones_dao = CalificacionesDAO()
login_dao = LoginDAO()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    usuario = data.get("usuario")
    password = data.get("password")
    
    resultado = login_dao.validar_credenciales(usuario, password)

    return jsonify({"login": resultado})


@app.route("/calificaciones/buscar")
def buscar_calificaciones():
    filas = calificaciones_dao.buscar_calificaciones()
    return jsonify(filas)


@app.route("/calificaciones/registrar", methods=["POST"])
def registrar_calificacion():
    data = request.json
    ok = calificaciones_dao.insertar_calificacion(
        data["matricula"],
        data["nombre"],
        data["calificacion"]
    )
    return jsonify({"ok": ok})


@app.route("/calificaciones/top1")
def top1():
    dato = calificaciones_dao.buscar_top1()
    return jsonify(dato)


@app.route("/alumnos/buscar")
def buscar_alumnos():
    filas = alumnos_dao.buscar_alumnos()
    return jsonify(filas)


@app.route("/alumnos/registrar", methods=["POST"])
def registrar_alumno():
    data = request.json
    ok = alumnos_dao.insertar_alumno(
        data["matricula"],
        data["nombre"]
    )
    return jsonify({"ok": ok})


@app.route("/")
def login_template():
    return render_template("login.html")


@app.route("/calificaciones")
def calificaciones_template():
    return render_template("calificaciones.html")


@app.route("/datos")
def datos_template():
    return render_template("datos.html")


if __name__ == "__main__":
    app.run(debug=True)
