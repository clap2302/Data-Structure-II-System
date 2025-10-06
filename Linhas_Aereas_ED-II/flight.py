from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

flight ={
    "flight_code": "",
    "origin": "",
    "destiny": "",
    "miles": "",
    "ticket_price": "",
    "airplane_type": "",
    "num_seats": ""
}

flight_management_page = """
<!doctype html>
<title>Gerenciamento de voo</title>
<h2>Gerenciamento de voo</h2>
<h3>Cadastro de voo</h3>
<form method="post">
  Código do voo: <input type="text" name="flight_code"><br>
  Origem: <input type="text" name="origin"><br>
  Destino: <input type="text" name="destiny"><br>
  Milhas percorridas: <input type="number" name="miles"><br>
  Preço da passagem: <input type="number" name="ticket_price"><br>
  Tipo do avião: <input type="text" name="airplane_type"><br>
  Número de assentos: <input type="number" name="num_seats"><br>
  <input type="submit" value="Cadastrar">
</form>
{% if erro %}
<p style="color:red;">{{ erro }}</p>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        flight_code = request.form["flight_code"]
        origin = request.form["origin"]
        destiny = request.form["destiny"]
        miles = request.form["miles"]
        ticket_price = request.form["ticket_price"]
        airplane_type = request.form["airplane_type"]
        num_seats = request.form["num_seats"]

    return render_template_string(flight_management_page, erro=erro)

if __name__ == "__main__":
    app.run(debug=True)
