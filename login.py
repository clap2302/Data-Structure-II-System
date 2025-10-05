from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# Dicionário de login/senha em memória

adms = {
    "admin": "1234",
    "funcionario": "abcd"
}
usuarios = {}

# Página de login
login_page = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post">
  Usuário: <input type="text" name="usuario"><br>
  Senha: <input type="password" name="senha"><br>
  <input type="submit" value="Entrar">
</form>
{% if erro %}
<p style="color:red;">{{ erro }}</p>
{% endif %}
"""

# Página administrativa
admin_page = """
<h2>Bem-vindo, {{ usuario }}!</h2>
<p>Gerencie os usuários:</p>

<h3>Adicionar usuário</h3>
<form method="post" action="/add_user">
  Usuário: <input type="text" name="usuario"><br>
  Senha: <input type="password" name="senha"><br>
  <input type="submit" value="Adicionar">
</form>

<h3>Remover usuário</h3>
<form method="post" action="/remove_user">
  Usuário: <input type="text" name="usuario"><br>
  <input type="submit" value="Remover">
</form>

<h3>Alterar senha</h3>
<form method="post" action="/change_password">
  Usuário: <input type="text" name="usuario"><br>
  Nova senha: <input type="password" name="nova_senha"><br>
  <input type="submit" value="Alterar Senha">
</form>

<h3>Usuários atuais</h3>
<ul>
{% for u in usuarios %}
  <li>{{ u }}</li>
{% endfor %}
</ul>

<a href="{{ url_for('logout') }}">Sair</a>
<p style="color:green;">{{ msg }}</p>
"""

# Página para usuários comuns
user_page = """
<h2>Bem-vindo, {{ usuario }}!</h2>
<p>Esta é a página do usuário comum. </p>
<a href="{{ url_for('logout') }}">Sair</a>
"""
# Rota de login
@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario in usuarios and usuarios[usuario] == senha:
            return redirect(url_for("user", usuario=usuario))

        elif usuario in adms and adms[usuario] == senha:
            return redirect(url_for("admin", usuario=usuario))
        
        else:
            erro = "Usuário ou senha incorretos"
    return render_template_string(login_page, erro=erro)

# Página administrativa
@app.route("/admin/<usuario>")
def admin(usuario):
    return render_template_string(admin_page, usuario=usuario, usuarios=usuarios.keys(), msg="")

# Página do usuário comum
@app.route("/user/<usuario>")
def user(usuario):
    return render_template_string(user_page, usuario=usuario)

# Adicionar usuário
@app.route("/add_user", methods=["POST"])
def add_user():
    usuario = request.form["usuario"]
    senha = request.form["senha"]
    msg = ""
    if usuario in usuarios:
        msg = "Usuário já existe!"
    else:
        usuarios[usuario] = senha
        msg = f"Usuário {usuario} adicionado!"
    return render_template_string(admin_page, usuario=usuario, usuarios=usuarios.keys(), msg=msg)

# Remover usuário
@app.route("/remove_user", methods=["POST"])
def remove_user():
    usuario = request.form["usuario"]
    msg = ""
    if usuario in usuarios:
        del usuarios[usuario]
        msg = f"Usuário {usuario} removido!"
    else:
        msg = "Usuário não existe!"
    return render_template_string(admin_page, usuario=usuario, usuarios=usuarios.keys(), msg=msg)

# Alterar senha
@app.route("/change_password", methods=["POST"])
def change_password():
    usuario = request.form["usuario"]
    nova_senha = request.form["nova_senha"]
    msg = ""
    if usuario in usuarios:
        usuarios[usuario] = nova_senha
        msg = f"Senha do usuário {usuario} alterada!"
    else:
        msg = "Usuário não existe!"
    return render_template_string(admin_page, usuario=usuario, usuarios=usuarios.keys(), msg=msg)

# Logout
@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
