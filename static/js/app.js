function activeMenuOption(href) {
    $(".app-menu .nav-link")
        .removeClass("active")
        .removeAttr('aria-current');

    $(`[href="${(href ? href : "#/")}"]`)
        .addClass("active")
        .attr("aria-current", "page");
}

// --- Funciones auxiliares simples ---
function disableAll() {
    $("button, input, select").attr("disabled", true);
}
function enableAll() {
    $("button, input, select").removeAttr("disabled");
}
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
app.controller("loginCtrl", function ($scope, $http, $rootScope) {
    $("#frmInicioSesion").off("submit").submit(function (event) {
        event.preventDefault();

        pop(".div-inicio-sesion", 'Iniciando sesión, espere...', "primary");
        disableAll();

        $.post("iniciarSesion", $(this).serialize(), function (respuesta) {
            enableAll();

            if (respuesta.length) {
                // ✅ Guardar el usuario activo correctamente
                localStorage.setItem("login", "1");
                localStorage.setItem("usuarioActivo", JSON.stringify(respuesta[0]));

                $("#frmInicioSesion").get(0).reset();

                // ✅ Redirigir a la página principal (calificaciones)
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
    // --- Validar si hay usuario logueado ---
    const usuario = JSON.parse(localStorage.getItem("usuarioActivo") || "null");
    if (!usuario) {
        alert("Por favor inicia sesión primero.");
        window.location.href = "#/";
        return;
    }

    let autoActualizar = false;

    function buscarCalificaciones(texto = "") {
        texto = texto.trim();
        if (texto === "") {
            $("#tbodyCalificacion").html("<tr><td colspan='3' class='text-center'>Ingresa algo para buscar</td></tr>");
            return;
        }

        $.get("/calificaciones/buscar", { busqueda: texto }, function (data) {
            let html = "";
            if (data.length > 0) {
                data.forEach(calificacion => {
                    html += `
                        <tr>
                            <td>${calificacion.idCalificacion}</td>
                            <td>${calificacion.idAlumno}</td>
                            <td>${calificacion.Calificacion}</td>
                        </tr>`;
                });
            } else {
                html = "<tr><td colspan='3' class='text-center'>No se encontraron resultados</td></tr>";
            }
            $("#tbodyCalificacion").html(html);
        });
    }

    $(document).on("click", "#btnBuscar", function () {
        const texto = $("#Contbuscar").val();
        buscarCalificaciones(texto);
    });

    $(document).on("keypress", "#Contbuscar", function (e) {
        if (e.which === 13) {
            $("#btnBuscar").click();
        }
    });

    Pusher.logToConsole = false;
    var pusher = new Pusher('505a9219e50795c4885e', { cluster: 'us2' });
    var channel = pusher.subscribe('for-nature-533');
    channel.bind('eventoApoyos', function(data) {
        if (autoActualizar) {
            buscarCalificaciones($("#Contbuscar").val());
        }
    });
});

document.addEventListener("DOMContentLoaded", function (event) {
    activeMenuOption(location.hash);
});
