from flask import Blueprint, request, render_template, redirect, url_for, session
from archives.data import users, adms

login_bp = Blueprint("login_bp", __name__)

# Rota de login
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        if user in users and users[user] == password:
            session["user"] = user
            session["role"] = "user"
            return redirect(url_for("flights_bp.flight_management"))

        elif user in adms and adms[user] == password:
            session["user"] = user
            session["role"] = "admin"
            return redirect(url_for("login_bp.admin_dashboard"))

        else:
            erro = "Usuário ou senha incorretos"
    return render_template("login_page.html", erro=erro)

# Página administrativa
@login_bp.route("/admin/<user>")
def admin(user):
    return render_template("admin_page.html", user=user, users=users.keys(), msg="")

# Página do usuário comum
@login_bp.route("/user/<user>")
def user(user):
    return render_template("user_page.html", user=user)

# Adicionar usuário
@login_bp.route("/add_user", methods=["POST"])
def add_user():
    user = request.form["user"]
    password = request.form["password"]
    msg = ""
    if user in users:
        msg = "Usuário já existe!"
    else:
        users[user] = password
        msg = f"Usuário {user} adicionado!"
    return render_template("admin_page.html", user=user, users=users.keys(), msg=msg)

# Remover usuário
@login_bp.route("/remove_user", methods=["POST"])
def remove_user():
    user = request.form["user"]
    msg = ""
    if user in users:
        del users[user]
        msg = f"Usuário {user} removido!"
    else:
        msg = "Usuário não existe!"
    return render_template("admin_page.html", user=user, users=users.keys(), msg=msg)

# Alterar senha
@login_bp.route("/change_password", methods=["POST"])
def change_password():
    user = request.form["user"]
    nova_password = request.form["new_password"]
    msg = ""
    if user in users:
        users[user] = nova_password
        msg = f"Senha do usuário {user} alterada!"
    else:
        msg = "Usuário não existe!"
    return render_template("admin_page.html", user=user, users=users.keys(), msg=msg)

# Logout
@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_bp.login"))

@login_bp.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return "Acesso negado", 403
    return render_template("admin_dashboard.html")

@login_bp.route("/register", methods=["POST"])
def register():
    user = request.form["user"]
    password = request.form["password"]
    msg = ""
    if user in users:
        msg = "Usuário já existe!"
    else:
        users[user] = password
        msg = f"Usuário {user} adicionado!"

    return render_template("register_page.html", user=user, users=users.keys(), msg=msg)

@login_bp.route("/register_page", methods=["GET"])
def register_page():
    return render_template("register_page.html")
