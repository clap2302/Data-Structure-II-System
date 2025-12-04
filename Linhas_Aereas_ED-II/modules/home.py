from flask import Blueprint, render_template, redirect, url_for, session
from modules.flight_manager import FlightManager

home_bp = Blueprint("home_bp", __name__)

@home_bp.route("/")
def home():
    user_role = session.get("role")
    user_name = session.get("user")
    reservations = {}

    if user_role == "user" and "reservations" in session:
        reservations = session["reservations"].get(user_name, [])

    flights = FlightManager.load_flights_dict()

    return render_template(
        "home.html",
        flights=flights
    )
