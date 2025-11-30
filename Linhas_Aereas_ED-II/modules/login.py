from flask import Blueprint, request, render_template, redirect, url_for, session
from archives.libs.btree_bib import BTree

login_bp = Blueprint("login_bp", __name__)

users_tree = BTree(t=2)
admins_tree = BTree(t=2)

# adm padrão
admins_tree.insert("admin", "1234")

def get_all_users():
    admins = [a for (a, _) in admins_tree.inorder()]
    users = [u for (u, _) in users_tree.inorder()]
    return admins + users

# login normal
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        # Login como usuário comum
        result_user = users_tree.search(users_tree.root, user)
        if result_user:
            node, idx = result_user
            if node.values[idx] == password:
                session["user"] = user
                session["role"] = "user"
                return redirect(url_for("flights_bp.flight_management"))

        # Login como administrador
        result_admin = admins_tree.search(admins_tree.root, user)
        if result_admin:
            node, idx = result_admin
            if node.values[idx] == password:
                session["user"] = user
                session["role"] = "admin"
                return redirect(url_for("login_bp.admin_dashboard"))

        erro = "Usuário ou senha incorretos"

    return render_template("login_page.html", erro=erro)

# se logar um adm, entra aqui
@login_bp.route("/admin/<user>")
def admin(user):
    users_list = get_all_users()
    return render_template("admin_page.html", user=user, users=users_list, msg="")

# se logar um usuario comum, entra aqui
@login_bp.route("/user/<user>")
def user_page(user):
    return render_template("user_page.html", user=user)


# funcoes para a pagina dos adms:

@login_bp.route("/add_user", methods=["POST"])
def add_user():
    user = request.form["user"]
    password = request.form["password"]
    role = request.form["role"]

    if users_tree.search(users_tree.root, user) or admins_tree.search(admins_tree.root, user):
        msg = "Usuário já existe!"
    else:
        if role == "user":
            users_tree.insert(user, password)
            msg = f"Usuário comum {user} adicionado!"
        else:
            admins_tree.insert(user, password)
            msg = f"Administrador {user} adicionado!"

    return render_template("admin_page.html", user="admin", users=get_all_users(), msg=msg)

@login_bp.route("/remove_user", methods=["POST"])
def remove_user():
    user = request.form["user"]

    if users_tree.search(users_tree.root, user):
        users_tree.remove(user)
        msg = f"Usuário comum {user} removido!"
    elif admins_tree.search(admins_tree.root, user):
        admins_tree.remove(user)
        msg = f"Administrador {user} removido!"
    else:
        msg = "Usuário não existe!"

    return render_template("admin_page.html", user="admin", users=get_all_users(), msg=msg)

@login_bp.route("/change_password", methods=["POST"])
def change_password():
    user = request.form["user"]
    nova_password = request.form["new_password"]

    if users_tree.update_password(user, nova_password):
        msg = f"Senha do usuário comum {user} alterada!"
    elif admins_tree.update_password(user, nova_password):
        msg = f"Senha do administrador {user} alterada!"
    else:
        msg = "Usuário não existe!"

    return render_template("admin_page.html", user="admin", users=get_all_users(), msg=msg)

@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_bp.login"))

# rota pra acessar a pagina do adms (so pra quem se logar)
@login_bp.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return "Acesso negado", 403

    return render_template("admin_dashboard.html")



# para a pag dos usuarios comuns

@login_bp.route("/register", methods=["POST"])
def register():
    user = request.form["user"]
    password = request.form["password"]

    if users_tree.search(users_tree.root, user) or admins_tree.search(admins_tree.root, user):
        msg = "Usuário já existe!"
    else:
        users_tree.insert(user, password)
        msg = f"Usuário {user} registrado!"

    return render_template("register_page.html", user=user, users=get_all_users(), msg=msg)


@login_bp.route("/register_page", methods=["GET"])
def register_page():
    return render_template("register_page.html")
