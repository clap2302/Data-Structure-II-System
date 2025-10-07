from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Dicionário de login/password em memória

adms = {
    "admin": "1234",
    "funcionario": "abcd"
}
users = {}

# Rota de login
@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        if user in users and users[user] == password:
            return redirect(url_for("user", user=user))

        elif user in adms and adms[user] == password:
            return redirect(url_for("admin", user=user))
        
        else:
            erro = "Usuário ou password incorretos"
    return render_template("login_page.html", erro=erro)

# Página administrativa
@app.route("/admin/<user>")
def admin(user):
    return render_template("admin_page.html", user=user, users=users.keys(), msg="")

# Página do usuário comum
@app.route("/user/<user>")
def user(user):
    return render_template("user_page.html", user=user)

# Adicionar usuário
@app.route("/add_user", methods=["POST"])
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
@app.route("/remove_user", methods=["POST"])
def remove_user():
    user = request.form["user"]
    msg = ""
    if user in users:
        del users[user]
        msg = f"Usuário {user} removido!"
    else:
        msg = "Usuário não existe!"
    return render_template("admin_page.html", user=user, users=users.keys(), msg=msg)

# Alterar password
@app.route("/change_password", methods=["POST"])
def change_password():
    user = request.form["user"]
    nova_password = request.form["new_password"]
    msg = ""
    if user in users:
        users[user] = nova_password
        msg = f"password do usuário {user} alterada!"
    else:
        msg = "Usuário não existe!"
    return render_template("admin_page.html", user=user, users=users.keys(), msg=msg)

# Logout
@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
