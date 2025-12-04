from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from modules.flight_manager import FlightManager
from modules.reservation_manager import ReservationManager
from functools import wraps

# Carrega o dicionário dos voos já convertido pelo FlightManager
flights = FlightManager.load_flights_dict()

flights_bp = Blueprint("flights_bp", __name__, url_prefix="/flights")


# ---------------------- DECORATORS ---------------------- #

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Acesso restrito a administradores.", "warning")
            return redirect(url_for("flights_bp.flight_management"))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Você precisa estar logado para ver esta página.", "info")
            return redirect(url_for("login_bp.login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------- LISTAGEM DE VOOS ---------------------- #

@flights_bp.route("/")
def flight_management():
    user_role = session.get("role", None)
    user_name = session.get("user", None)

    all_reservations = ReservationManager.load_reservations()

    user_reservations = all_reservations.get(user_name, []) if user_role == "user" else []

    return render_template(
        "flight_management.html",
        flights=flights,
        role=user_role,
        reservations=user_reservations
    )


# ---------------------- ADICIONAR VOO ---------------------- #

@flights_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_flight():
    global flights

    if request.method == "POST":
        flight_code = request.form["flight_code"]

        if flight_code in flights:
            return render_template("add_flight.html", error="Já existe um voo com esse código!")

        flights[flight_code] = {
            "origin": request.form["origin"],
            "destiny": request.form["destiny"],
            "miles": int(request.form["miles"]),
            "ticket_price": float(request.form["ticket_price"]),     # OK
            "airplane_type": request.form["airplane_type"],
            "num_seats": int(request.form["num_seats"]),
            "reserved": 0,
            "flight_datetime": request.form["flight_datetime"],      # OK
            "duration": int(request.form["duration"])                # OK
        }

        FlightManager.save_flights_dict(flights)
        return redirect(url_for("flights_bp.flight_management"))

    return render_template("add_flight.html")


# ---------------------- EDITAR VOO ---------------------- #

@flights_bp.route("/edit/<flight_code>", methods=["GET", "POST"])
@admin_required
def edit_flight(flight_code):
    global flights

    if flight_code not in flights:
        return "Voo não encontrado", 404

    if request.method == "POST":
        flights[flight_code].update({
            "origin": request.form["origin"],
            "destiny": request.form["destiny"],
            "miles": int(request.form["miles"]),
            "ticket_price": float(request.form["ticket_price"]),
            "airplane_type": request.form["airplane_type"],
            "num_seats": int(request.form["num_seats"]),
            "flight_datetime": request.form["flight_datetime"],
            "duration": int(request.form["duration"])
        })

        FlightManager.save_flights_dict(flights)
        return redirect(url_for("flights_bp.flight_management"))

    return render_template("edit_flight.html", flight_code=flight_code, flight=flights[flight_code])


# ---------------------- DELETAR VOO ---------------------- #

@flights_bp.route("/delete/<flight_code>", methods=["POST"])
@admin_required
def delete_flight(flight_code):
    global flights

    if flight_code in flights:
        del flights[flight_code]

    FlightManager.save_flights_dict(flights)
    return redirect(url_for("flights_bp.flight_management"))


# ---------------------- RESERVAR VOO ---------------------- #

@flights_bp.route("/reserve/<flight_code>", methods=["POST"])
def reserve_flight(flight_code):
    if session.get("role") != "user":
        return "Acesso negado", 403

    user = session.get("user")

    if not user:
        return redirect(url_for("login_bp.login"))

    ReservationManager.add_reservation(user, flight_code)

    return redirect(url_for("flights_bp.flight_management"))
