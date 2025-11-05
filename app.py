# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector

import datetime
import pytz

from flask_cors import CORS, cross_origin

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_23005116_bd",
    user="u760464709_23005116_usr",
    password="z8[T&05u"
)

app = Flask(__name__)
CORS(app)

def pusherApoyos():
    import pusher

    pusher_client = pusher.Pusher(
      app_id='1891402',
      key='505a9219e50795c4885e',
      secret='fac4833b05652932a8bc',
      cluster='us2',
      ssl=True
    )
    
    pusher_client.trigger("for-nature-533", "eventoApoyos", {"message": "Hola Mundo!"})
    return make_response(jsonify({}))


@app.route("/")
def index():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("index.html")

@app.route("/app")
def app2():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("login.html")
    # return "<h5>Hola, soy la view app</h5>"

@app.route("/iniciarSesion", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def iniciarSesion():
    if not con.is_connected():
        con.reconnect()

    usuario    = request.form["txtUsuario"]
    contrasena = request.form["txtContrasena"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Usuario
    FROM usuarios

    WHERE Nombre_Usuario = %s
    AND Contrasena = %s
    """
    val    = (usuario, contrasena)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/apoyos")
def apoyos():
    return render_template("apoyos.html")

@app.route("/tbodyApoyo")
def tbodyApoyo():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idApoyo,
           idMascota,
           idPadrino,
           monto,
           causa	

    FROM apoyos

    ORDER BY idApoyo DESC

    LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    # Si manejas fechas y horas
    """
    for registro in registros:
        fecha_hora = registro["Fecha_Hora"]

        registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
        registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
    """

    return render_template("tbodyApoyo.html", apoyos=registros)

@app.route("/productos/ingredientes/<int:idApoyo>")
def productosIngredientes(id):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT productos.Nombre_Producto, ingredientes.*, productos_ingredientes.Cantidad FROM productos_ingredientes
    INNER JOIN productos ON productos.Id_Producto = productos_ingredientes.Id_Producto
    INNER JOIN ingredientes ON ingredientes.Id_Ingrediente = productos_ingredientes.Id_Ingrediente
    WHERE productos_ingredientes.Id_Producto = %s
    ORDER BY productos.Nombre_Producto
    """

    cursor.execute(sql, (id, ))
    registros = cursor.fetchall()

    return render_template("modal.html", productosIngredientes=registros)

@app.route("/mascotas")
def listarMascotas():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = "SELECT idMascota, nombre FROM mascotas ORDER BY nombre"
    cursor.execute(sql)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/padrinos")
def listarPadrinos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = "SELECT idPadrino, nombrePadrino FROM padrinos ORDER BY nombrePadrino"
    cursor.execute(sql)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))


@app.route("/apoyos/buscar", methods=["GET"])
def buscarApoyos():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idApoyo,
           idMascota,
           idPadrino,
           monto,
           causa	

    FROM apoyos

    WHERE idMascota LIKE %s
    OR    idPadrino LIKE %s
    OR    monto     LIKE %s
    OR    causa     LIKE %s

    ORDER BY idApoyo DESC

    LIMIT 10 OFFSET 0
    """
    val    = (busqueda, busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

        # Si manejas fechas y horas
        """
        for registro in registros:
            fecha_hora = registro["Fecha_Hora"]

            registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
            registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
        """

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        con.close()

    return make_response(jsonify(registros))

@app.route("/apoyo", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def guardarApoyo():
    if not con.is_connected():
        con.reconnect()

    idApoyo    = request.form["idApoyo"]
    idMascota  = request.form["mascota"]
    padrino    = request.form["padrino"]
    monto      = request.form["monto"]
    causa      = request.form["causa"]
    # fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if idApoyo:
        sql = """
        UPDATE apoyos

        SET idMascota = %s,
        idPadrino = %s,
        monto     = %s,
        causa     = %s

        WHERE idApoyo = %s
        """
        val = (idMascota, padrino, monto, causa, idApoyo)
    else:
        sql = """
        INSERT INTO apoyos (idMascota, idPadrino, monto, causa)
                    VALUES    (%s,          %s,      %s,    %s)
        """
        val =                 (idMascota, padrino, monto, causa)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusherApoyos()
    
    return make_response(jsonify({}))

@app.route("/apoyo/<int:idApoyo>")
def editarApoyos(idApoyo):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idApoyo, idMascota, idPadrino, monto, causa

    FROM apoyos

    WHERE idApoyo = %s
    """
    val    = (idApoyo,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/apoyo/eliminar", methods=["POST"])
def eliminarApoyo():
    if not con.is_connected():
        con.reconnect()

    idApoyo = request.form["idApoyo"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM apoyos
    WHERE idApoyo = %s
    """
    val    = (idApoyo,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))















