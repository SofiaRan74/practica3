function activeMenuOption(href) {
    $(".app-menu .nav-link")
        .removeClass("active")
        .removeAttr('aria-current');

    $(`[href="${(href ? href : "#/")}"]`)
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


app.controller("appCtrl", function ($scope, $http, $window) {

    $scope.usuario = "";
    $scope.contrasena = "";
    $scope.mensajeError = "";

    $scope.iniciarSesion = function () {
        if (!$scope.usuario || !$scope.contrasena) {
            $scope.mensajeError = "Por favor ingresa usuario y contraseña.";
            return;
        }

        const datos = new FormData();
        datos.append("txtUsuario", $scope.usuario);
        datos.append("txtContrasena", $scope.contrasena);

        fetch("/iniciarSesion", {
            method: "POST",
            body: datos
        })
        .then(res => res.json())
        .then(data => {
            if (data.length > 0) {
                
                $scope.mensajeError = "";
                localStorage.setItem("usuarioActivo", JSON.stringify(data[0]));
                $window.location.href = "#/calificaciones";
            } else {

                $scope.mensajeError = "Usuario o contraseña incorrectos.";
            }
            $scope.$apply();
        })
        .catch(err => {
            console.error("Error en el login:", err);
            $scope.mensajeError = "Error al conectar con el servidor.";
            $scope.$apply();
        });
    };

});


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
            // si no hay texto, limpiar tabla
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
                        </tr>
                    `;
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

