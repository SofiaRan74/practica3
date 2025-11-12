function activeMenuOption(href) {
    $("#appMenu .nav-link")
        .removeClass("active")
        .removeAttr('aria-current')

    $(`[href="${(href ? href : "#/")}"]`)
        .addClass("active")
        .attr("aria-current", "page")
}

function disableAll() {
    const elements = document.querySelectorAll(".while-waiting")
    elements.forEach(function (el) {
        el.setAttribute("disabled", "true")
        el.classList.add("disabled")
    })
}

function enableAll() {
    const elements = document.querySelectorAll(".while-waiting")
    elements.forEach(function (el) {
        el.removeAttribute("disabled")
        el.classList.remove("disabled")
    })
}

function debounce(fun, delay) {
    let timer
    return function (...args) {
        clearTimeout(timer)
        timer = setTimeout(function () {
            fun.apply(this, args)
        }, delay)
    }
}

const DateTime = luxon.DateTime
let lxFechaHora
let diffMs = 0
const configFechaHora = {
    locale: "es",
    weekNumbers: true,
    minuteIncrement: 15,
    altInput: true,
    altFormat: "d/F/Y",
    dateFormat: "Y-m-d",
}

const app = angular.module("angularjsApp", ["ngRoute"])

/* ──────────────── SERVICIOS ──────────────── */
app.service("SesionService", function () {
    this.tipo = null
    this.usr = null

    this.setTipo = function (tipo) { this.tipo = tipo }
    this.getTipo = function () { return this.tipo }

    this.setUsr = function (usr) { this.usr = usr }
    this.getUsr = function () { return this.usr }
})

app.factory("CategoriaFactory", function () {
    function Categoria(titulo, productos) {
        this.titulo = titulo
        this.productos = productos
    }

    Categoria.prototype.getInfo = function () {
        return {
            titulo: this.titulo,
            productos: this.productos
        }
    }

    return {
        create: function (titulo, productos) {
            return new Categoria(titulo, productos)
        }
    }
})

app.service("MensajesService", function () {
    this.modal = modal
    this.pop = pop
    this.toast = toast
})

app.service("CalificacionAPI", function ($q) {
    this.buscarCalificaciones = function () {
        const deferred = $q.defer();
        $.get("calificaciones/buscar")
            .done(data => deferred.resolve(data))
            .fail(err => deferred.reject(err));
        return deferred.promise;
    };
});

app.factory("CalificacionFactory", function () {
    function Calificacion(idCalificacion, nombrecompleto, valorCalificacion, categoria) {
        this.idCalificacion = idCalificacion;
        this.NombreCompleto = nombrecompleto;
        this.Calificacion = valorCalificacion;
        this.Categoria = categoria;
    }

    Calificacion.prototype.getInfo = function () {
        return {
            idCalificacion: this.idCalificacion,
            NombreCompleto: this.NombreCompleto,
            Calificacion: this.Calificacion,
            Categoria: this.Categoria
        };
    };

    return {
        create: function (idCalificacion, nombrecompleto, valorCalificacion, categoria) {
            return new Calificacion(idCalificacion, nombrecompleto, valorCalificacion, categoria);
        }
    };
});

app.factory("CalificacionDecorator", function () {
    function decorate(calificacion, extraData) {
        calificacion.fecha = extraData?.fecha || new Date().toISOString();
        calificacion.comentario = extraData?.comentario || "Sin comentarios";

        calificacion.esExcelente = function () {
            return this.Calificacion >= 90;
        };

        calificacion.getInfoDetallada = function () {
            return {
                idCalificacion: this.idCalificacion,
                NombreCompleto: this.NombreCompleto,
                Calificacion: this.Calificacion,
                Categoria: this.Categoria,
                esExcelente: this.esExcelente(),
                fecha: this.fecha,
                comentario: this.comentario
            };
        };

        return calificacion;
    }

    return { decorate: decorate };
});

app.factory("CalificacionFacade", function (CalificacionAPI, CalificacionFactory, CalificacionDecorator, $q) {
    return {
        obtenerCalificaciones: function () {
            const deferred = $q.defer();

            CalificacionAPI.buscarCalificaciones()
                .then(function (data) {
                    const calificacionesDecoradas = data.map(c => {
                        let calificacion = CalificacionFactory.create(
                            c.idCalificacion,
                            c.NombreCompleto,
                            c.Calificacion,
                            c.Categoria
                        );

                        const extraData = {
                            fecha: c.fecha || new Date().toISOString(),
                            comentario: c.comentario || "Sin comentarios"
                        };

                        return CalificacionDecorator.decorate(calificacion, extraData);
                    });

                    deferred.resolve(calificacionesDecoradas);
                })
                .catch(err => deferred.reject(err));

            return deferred.promise;
        },

        obtenerTopTres: function () {
            const deferred = $q.defer();

            this.obtenerCalificaciones()
                .then(function (calificaciones) {
                    const topTres = calificaciones
                        .sort((a, b) => b.Calificacion - a.Calificacion)
                        .slice(0, 3);

                    deferred.resolve(topTres);
                })
                .catch(err => deferred.reject(err));

            return deferred.promise;
        }
    };
});

/* ──────────────── CONFIGURACIÓN DE RUTAS ──────────────── */
app.config(function ($routeProvider, $locationProvider, $provide) {
    $provide.decorator("MensajesService", function ($delegate) {
        const originalModal = $delegate.modal;
        const originalPop = $delegate.pop;
        const originalToast = $delegate.toast;

        $delegate.modal = function (msg) {
            originalModal(msg, "Mensaje", [
                {
                    html: "Aceptar",
                    class: "btn btn-lg btn-secondary",
                    defaultButton: true,
                    dismiss: true
                }
            ]);
        };

        $delegate.pop = function (msg) {
            $(".div-temporal").remove();
            $("body").prepend($("<div />", { class: "div-temporal" }));
            originalPop(".div-temporal", msg, "info");
        };

        $delegate.toast = function (msg) {
            originalToast(msg, 2);
        };

        return $delegate;
    });

    $locationProvider.hashPrefix("");

    $routeProvider
        .when("/", {
            templateUrl: "login",
            controller: "loginCtrl"
        })
        .when("/calificaciones", {
            templateUrl: "calificaciones",
            controller: "CalificacionesCtrl"
        })
        .otherwise({
            redirectTo: "/"
        });
});

/* ──────────────── CONTROLADORES ──────────────── */
app.controller("loginCtrl", function ($scope, $http, $rootScope) {
    $("#frmInicioSesion").submit(function (event) {
        event.preventDefault()

        pop(".div-inicio-sesion", 'ℹ️ Iniciando sesión, espere un momento...', "primary")

        $.post("iniciarSesion", $(this).serialize(), function (respuesta) {
            enableAll()

            if (respuesta.length) {
                localStorage.setItem("login", "1")
                localStorage.setItem("preferencias", JSON.stringify(respuesta[0]))
                $("#frmInicioSesion").get(0).reset()
                location.reload()
                return
            }

            pop(".div-inicio-sesion", "Usuario y/o contraseña incorrecto(s)", "danger")
        })

        disableAll()
    })
})

app.controller("CalificacionesCtrl", function ($scope, CalificacionFacade, MensajesService, SesionService) {
    $scope.calificaciones = [];
    $scope.topTres = [];
    $scope.SesionService = SesionService;

    $scope.cargarCalificaciones = function () {
        CalificacionFacade.obtenerCalificaciones()
            .then(function (data) {
                $scope.calificaciones = data;
                $scope.calificaciones.sort((a, b) => b.Calificacion - a.Calificacion);
                MensajesService.toast("✅ Calificaciones cargadas correctamente");
            })
            .catch(function (error) {
                console.error("❌ Error al obtener calificaciones:", error);
                MensajesService.modal("No se pudieron cargar las calificaciones.");
            });
    };

    $scope.cargarTopTres = function () {
        CalificacionFacade.obtenerTopTres()
            .then(function (top3) {
                $scope.topTres = top3;
                MensajesService.toast("🏆 Top 3 de calificaciones listo");
            })
            .catch(function (error) {
                console.error("❌ Error al obtener Top 3:", error);
                MensajesService.modal("Error al cargar el Top 3 de calificaciones.");
            });
    };

    $scope.verDetalles = function (c) {
        alert(
            "Detalles del alumno:\n" +
            "Nombre: " + c.NombreCompleto + "\n" +
            "Calificación: " + c.Calificacion + "\n" +
            "Categoría: " + c.Categoria
        );
    };

    $scope.init = function () {
        $scope.cargarCalificaciones();
        $scope.cargarTopTres();
    };

    $scope.init();
});

/* ──────────────── DOCUMENT READY ──────────────── */
document.addEventListener("DOMContentLoaded", function () {
    activeMenuOption(location.hash);
});
