function activeMenuOption(href) {
    $(".app-menu .nav-link")
        .removeClass("active")
        .removeAttr('aria-current');

    $(`[href="${(href ? href : "#/")}"]`)
        .addClass("active")
        .attr("aria-current", "page");
}

// --- Funciones auxiliares simples ---
function disableAll() { $("button, input, select").attr("disabled", true); }
function enableAll() { $("button, input, select").removeAttr("disabled"); }
function pop(selector, mensaje, tipo = "info") {
    $(selector).html(`<div class="alert alert-${tipo} mt-2">${mensaje}</div>`);
}

const app = angular.module("angularjsApp", ["ngRoute"]);

app.config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("");

    $routeProvider
        .when("/", {
            templateUrl: "login",
            controller: "loginCtrl"
        })
        .when("/calificaciones", {
            templateUrl: "/calificaciones",
            controller: "calificacionesCtrl"
        })
        .otherwise({
            redirectTo: "/"
        });
});

// --- Controlador del login ---
app.controller("loginCtrl", function ($scope, $http) {
    $("#frmInicioSesion").off("submit").submit(function (event) {
        event.preventDefault();

        pop(".div-inicio-sesion", 'Iniciando sesión, espere...', "primary");
        disableAll();

        $.post("iniciarSesion", $(this).serialize(), function (respuesta) {
            enableAll();

            if (respuesta.length) {
                localStorage.setItem("login", "1");
                localStorage.setItem("usuarioActivo", JSON.stringify(respuesta[0]));

                $("#frmInicioSesion")[0].reset();

                window.location.href = "#/calificaciones";
                return;
            }

            pop(".div-inicio-sesion", "Usuario y/o contraseña incorrectos", "danger");
        }).fail(function () {
            enableAll();
            pop(".div-inicio-sesion", "Error al conectar con el servidor", "danger");
        });
    });
});

// --- Controlador de calificaciones ---
app.controller("calificacionesCtrl", function ($scope, $http) {
    // Validar sesión
    const usuario = JSON.parse(localStorage.getItem("usuarioActivo") || "null");
    if (!usuario) {
        alert("Debes iniciar sesión primero.");
        window.location.href = "#/";
        return;
    }

    let autoActualizar = false;

    function mostrarCargando() {
        $("#tbodyCalificacion").html(`<tr>
            <th colspan="3" class="text-center">
                <div class="spinner-border" style="width:3rem; height:3rem;" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </th>
        </tr>`);
    }

    function buscarCalificaciones(texto = "") {
        mostrarCargando();

        $.get("/calificaciones/buscar", { busqueda: texto }, function (data) {
            enableAll();
            let html = "";

            if (data.length > 0) {
                data.forEach(c => {
                    html += `
                        <tr>
                            <td>${c.idCalificacion}</td>
                            <td>${c.idAlumno}</td>
                            <td>${c.Calificacion}</td>
                        </tr>`;
                });
            } else {
                html = "<tr><td colspan='3' class='text-center'>No se encontraron resultados</td></tr>";
            }

            $("#tbodyCalificacion").html(html);
        }).fail(function() {
            alert("Error al cargar calificaciones");
        });

        disableAll();
    }

    // Buscar al cargar
    buscarCalificaciones();

    // Eventos
    $(document).on("click", "#btnBuscar", function () {
        buscarCalificaciones($("#Contbuscar").val());
    });

    $(document).on("keypress", "#Contbuscar", function (e) {
        if (e.which === 13) {
            $("#btnBuscar").click();
        }
    });

    // --- Pusher para actualización automática ---
    Pusher.logToConsole = false;
    var pusher = new Pusher('505a9219e50795c4885e', { cluster: 'us2' });
    var channel = pusher.subscribe('for-nature-533');
    channel.bind('eventoApoyos', function (data) {
        if (autoActualizar) {
            buscarCalificaciones($("#Contbuscar").val());
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    activeMenuOption(location.hash);
});
