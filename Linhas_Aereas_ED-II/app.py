from flask import Flask

from modules.login import login_bp
from modules.flights import flights_bp

app = Flask(__name__)

app.secret_key = "ed2-flask-secret-key"

app.register_blueprint(login_bp)
app.register_blueprint(flights_bp)

if __name__ == "__main__":
    app.run(debug=True)
