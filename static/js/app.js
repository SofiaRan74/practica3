function activeMenuOption(href) {
    $(".app-menu .nav-link")
        .removeClass("active")
        .removeAttr("aria-current");

    $(`[href="${href ? href : "#/"}"]`)
        .addClass("active")
        .attr("aria-current", "page");
}

const app = angular.module("angularjsApp", ["ngRoute"]);

app.config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("");

    $routeProvider
        .when("/", {
            templateUrl: "/app",
            controller: "appCtrl"
        })
        .when("/calificaciones", {
            templateUrl: "/calificaciones",
            controller: "calificacionesCtrl"
        })
        .otherwise({
            redirectTo: "/"
        });
});

app.controller("appCtrl", function ($scope, $http) {
    // Controlador vacío para "/"
});


// --- Controlador de calificaciones ---
app.controller("calificacionesCtrl", function ($scope, $http) {

    let autoActualizar = false;
    function buscarCalificaciones(texto = "") {
        $.get("/calificaciones/buscar", { busqueda: texto }, function (data) {
            let html = "";

            if (data.length === 0) {
                html = `<tr><td colspan="3" class="text-center">No se encontraron resultados</td></tr>`;
            } else {
                data.forEach(calificacion => {
                    html += `
                        <tr>
                            <td>${calificacion.idCalificacion}</td>
                            <td>${calificacion.idAlumno}</td>
                            <td>${calificacion.Calificacion}</td>
                        </tr>
                    `;
                });
            }

            $("#tbodyCalificacion").html(html);
        }).fail(function () {
            $("#tbodyCalificacion").html(`<tr><td colspan="3" class="text-center text-danger">Error al obtener datos</td></tr>`);
        });
    }

    buscarCalificaciones();

    $(document).on("click", "#btnBuscar", function () {
        const texto = $("#Contbuscar").val();
        buscarCalificaciones(texto);
    });

    Pusher.logToConsole = false;
    var pusher = new Pusher("505a9219e50795c4885e", { cluster: "us2" });
    var channel = pusher.subscribe("for-nature-533");
    channel.bind("eventoApoyos", function (data) {
        if (autoActualizar) {
            buscarCalificaciones();
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    activeMenuOption(location.hash);
});
