from flask import Flask, request, render_template, redirect, url_for
from archives.data import flights

app = Flask(__name__)

@app.route("/")
def flight_management():
    return render_template("flight_management.html", flights=flights)

@app.route("/add", methods=["GET", "POST"])
def add_flight():
    if request.method == "POST":
        flight_code = request.form["flight_code"]

        # Evita sobrescrever voo existente
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
        return redirect(url_for("flight_management"))

    return render_template("add_flight.html")

@app.route("/edit/<flight_code>", methods=["GET", "POST"])
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
        return redirect(url_for("flight_management"))

    return render_template("edit_flight.html", flight_code=flight_code, flight=flights[flight_code])

@app.route("/delete/<flight_code>", methods=["POST"])
def delete_flight(flight_code):
    if flight_code in flights:
        del flights[flight_code]
    return redirect(url_for("flight_management"))

if __name__ == "__main__":
    app.run(debug=True)
