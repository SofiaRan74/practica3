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
        .when("/apoyos", {
            templateUrl: "/apoyos",
            controller: "apoyosCtrl"
        })
        .otherwise({
            redirectTo: "/"
        });
});

app.controller("appCtrl", function ($scope, $http) {
    // Controlador vacío para "/" si necesitas
});

// --- controlador de apoyos ---
app.controller("apoyosCtrl", function ($scope, $http) {

    let autoActualizar = false;

    // función para cargar la tabla
    function buscarApoyos(texto = "") {
        if (texto.trim() === "") {
            $.get("/tbodyApoyo", function (trsHTML) {
                $("#tbodyApoyo").html(trsHTML);
            });
        } else {
            $.get("/apoyos/buscar", { busqueda: texto }, function (data) {
                let html = "";
                data.forEach(apoyo => {
                    html += `
                        <tr>
                            <td>${apoyo.idApoyo}</td>
                            <td>${apoyo.idMascota}</td>
                            <td>${apoyo.idPadrino}</td>
                            <td>${apoyo.monto}</td>
                            <td>${apoyo.causa}</td>
                            <td><button class="btn btn-info btn-editar" data-id="${ apoyo.idApoyo }">Editar</button></td>
                            <td><button class="btn btn-info btn-eliminar" data-id="${ apoyo.idApoyo }">Eliminar</button></td>  
                        </tr>
                    `;
                });
                $("#tbodyApoyo").html(html);
            });
        }
    }

    // cargar datos iniciales
    buscarApoyos();
    cargarMascotas();
    cargarPadrinos();

    // --- búsqueda ---
    $(document).on("click", "#btnBuscar", function () {
        const texto = $("#Contbuscar").val();
        buscarApoyos(texto);
    });

    // --- editar ---
    $(document).on("click", ".btn-editar", function () {
        const id = $(this).data("id");

        $.get("/apoyo/" + id, function (respuesta) {
            if (respuesta.length > 0) {
                const apoyo = respuesta[0];
                $("#idApoyo").val(apoyo.idApoyo);
                $("#mascota").val(apoyo.idMascota);
                $("#padrino").val(apoyo.idPadrino);
                $("#monto").val(apoyo.monto);
                $("#causa").val(apoyo.causa);
            }
        })
    })

    // --- guardar (insertar o actualizar) ---
    $(document).on("submit", "#frmApoyo", function (event) {
        event.preventDefault();

        $.post("/apoyo", {
            idApoyo: $("#idApoyo").val(),
            mascota: $("#mascota").val(),
            padrino: $("#padrino").val(),
            monto: $("#monto").val(),
            causa: $("#causa").val(),
        }, function () {
            buscarApoyos();
            $("#frmApoyo")[0].reset();
            $("#idApoyo").val(""); // limpiar idApoyo para el próximo insert
        }).fail(function(xhr) {
            alert("Error al guardar: " + xhr.responseText);
        });
    });

    // --- eliminar ---
    $(document).off("click", ".btn-eliminar").on("click", ".btn-eliminar", function () {
        const idApoyo = $(this).data("id");

        if (!confirm("¿Seguro que deseas eliminar este apoyo?")) {
            return;
        }

        $.post("/apoyo/eliminar", { idApoyo: idApoyo }, function () {
            buscarApoyos();
        }).fail(function(xhr) {
            alert("Error al eliminar: " + xhr.responseText);
        });
    });

    // --- Pusher para actualización automática ---
    Pusher.logToConsole = true;
    var pusher = new Pusher('505a9219e50795c4885e', { cluster: 'us2' });
    var channel = pusher.subscribe('for-nature-533');
    channel.bind('eventoApoyos', function(data) {
        if (autoActualizar) {
            buscarApoyos();
        }
    });
});

// --- funciones auxiliares para llenar selects ---
function cargarMascotas() {
    $.get("/mascotas", function (data) {
        const $select = $("#mascota");
        $select.empty().append('<option value="">Selecciona una mascota</option>');
        data.forEach(m => $select.append(`<option value="${m.idMascota}">${m.nombre}</option>`));
    });
}

function cargarPadrinos() {
    $.get("/padrinos", function (data) {
        const $select = $("#padrino");
        $select.empty().append('<option value="">Selecciona un padrino</option>');
        data.forEach(p => $select.append(`<option value="${p.idPadrino}">${p.nombrePadrino}</option>`));
    });
}

document.addEventListener("DOMContentLoaded", function (event) {
    activeMenuOption(location.hash);
});



