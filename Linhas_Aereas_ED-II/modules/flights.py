from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from functools import wraps
from archives.data import flights

flights_bp = Blueprint("flights_bp", __name__, url_prefix="/flights")

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


@flights_bp.route("/")
def flight_management():
    user_role = session.get("role", None)
    user_name = session.get("user", None)
    reservations = {}

    if user_role == "user" and "reservations" in session:
        reservations = session["reservations"].get(user_name, [])

    return render_template(
        "flight_management.html",
        flights=flights,
        role=user_role,
        reservations=reservations
    )


@flights_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_flight():
    if request.method == "POST":
        flight_code = request.form["flight_code"]
        if flight_code in flights:
            return render_template("add_flight.html", error="Já existe um voo com esse código!")

        flights[flight_code] = {
            "origin": request.form["origin"],
            "destiny": request.form["destiny"],
            "miles": request.form["miles"],
            "ticket_price": request.form["ticket_price"],
            "airplane_type": request.form["airplane_type"],
            "num_seats": request.form["num_seats"]
        }
        return redirect(url_for("flights_bp.flight_management"))

    return render_template("add_flight.html")

@flights_bp.route("/edit/<flight_code>", methods=["GET", "POST"])
@admin_required
def edit_flight(flight_code):
    if flight_code not in flights:
        return "Voo não encontrado", 404

    if request.method == "POST":
        flights[flight_code].update({
            "origin": request.form["origin"],
            "destiny": request.form["destiny"],
            "miles": request.form["miles"],
            "ticket_price": request.form["ticket_price"],
            "airplane_type": request.form["airplane_type"],
            "num_seats": request.form["num_seats"]
        })
        return redirect(url_for("flights_bp.flight_management"))

    return render_template("edit_flight.html", flight_code=flight_code, flight=flights[flight_code])

@flights_bp.route("/delete/<flight_code>", methods=["POST"])
@admin_required
def delete_flight(flight_code):
    if flight_code in flights:
        del flights[flight_code]
    return redirect(url_for("flights_bp.flight_management"))

@flights_bp.route("/reserve/<flight_code>", methods=["POST"])
def reserve_flight(flight_code):
    if session.get("role") != "user":
        return "Acesso negado", 403

    user = session.get("user")
    if not user:
        return redirect(url_for("login_bp.login"))

    # Criar o dicionário se não existir
    if "reservations" not in session:
        session["reservations"] = {}

    # Pegar as reservas atuais do usuário
    user_reservations = session["reservations"].get(user, [])

    # Evitar duplicar
    if flight_code not in user_reservations:
        user_reservations.append(flight_code)
        session["reservations"][user] = user_reservations

    session.modified = True
    return redirect(url_for("flights_bp.flight_management"))
