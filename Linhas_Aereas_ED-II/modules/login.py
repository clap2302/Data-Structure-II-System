from flask import Blueprint, request, render_template, redirect, url_for, session
from archives.libs.btree_bib import BTree
from modules.csv_manager import CSVManager

login_bp = Blueprint("login_bp", __name__)

# Árvores primárias
users_by_cpf = BTree(t=2)     # principal
users_by_name = BTree(t=2)    # secundária

admins_tree = BTree(t=2)

# Carregar todos os usuários do CSV e preencher árvores
all_users = CSVManager.get_users()

for idx, user in enumerate(all_users):
    csv_line = idx + 1

    cpf = user["cpf"]
    nome = user["name"]

    users_by_cpf.insert(cpf, csv_line)
    users_by_name.insert(nome, csv_line)

# Admin padrão
admins_tree.insert("admin", "1234")


# -----------------------
# FUNÇÃO AUXILIAR
# -----------------------

def load_user_from_csv(line_number: int):
    """Retorna o usuário correspondente à linha no CSV."""
    users = CSVManager.get_users()
    if 0 < line_number <= len(users):
        return users[line_number - 1]
    return None


# -----------------------
# LOGIN
# -----------------------
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        user_cpf = request.form["user"]       # Agora CPF
        password = request.form["password"]

        # ===== LOGIN COMO USUÁRIO COMUM =====
        result_user = users_by_cpf.search(users_by_cpf.root, user_cpf)
        if result_user:
            node, idx = result_user
            line_number = node.values[idx]   # posição no CSV
            user_data = load_user_from_csv(line_number)

            if user_data and user_data["password"] == password:
                session["user"] = user_data["user"]
                session["cpf"] = user_cpf
                session["role"] = "user"
                return redirect(url_for("flights_bp.flight_management"))

        # ===== LOGIN COMO ADMIN =====
        result_admin = admins_tree.search(admins_tree.root, user_cpf)
        if result_admin:
            node, idx = result_admin
            if node.values[idx] == password:
                session["user"] = user_cpf
                session["role"] = "admin"
                return redirect(url_for("login_bp.admin_dashboard"))

        # Se não encontrou nada
        erro = "CPF ou senha incorretos"

    return render_template("login_page.html", erro=erro)


# -----------------------
# PAINEL DE ADMIN
# -----------------------
@login_bp.route("/admin/<user>")
def admin(user):
    users_list = CSVManager.get_users()
    return render_template("admin_page.html", user=user, users=users_list, msg="")


@login_bp.route("/user/<user>")
def user_page(user):
    return render_template("user_page.html", user=user)


# -----------------------
# CRUD DE USUÁRIOS
# -----------------------

@login_bp.route("/add_user", methods=["POST"])
def add_user():
    name = request.form["name"]
    cpf = request.form["cpf"]       # chave principal
    user = request.form["user"]
    password = request.form["password"]
    role = request.form["role"]
    miles = 0

    # Impede duplicações
    if users_by_cpf.search(users_by_cpf.root, cpf) or admins_tree.search(admins_tree.root, user):
        msg = "Usuário já existe!"
        return render_template("admin_page.html", user="admin", users=CSVManager.get_users(), msg=msg)

    # Usuário comum
    if role == "user":
        line = CSVManager.add_user([name, user, password, cpf, miles])
        users_by_cpf.insert(cpf, line)
        users_by_name.insert(name, line)
        msg = f"Usuário {user} adicionado!"

    # Administrador
    else:
        admins_tree.insert(user, password)
        msg = f"Administrador {user} adicionado!"

    return render_template("admin_page.html", user="admin", users=CSVManager.get_users(), msg=msg)


@login_bp.route("/remove_user", methods=["POST"])
def remove_user():
    cpf = request.form["cpf"]

    result = users_by_cpf.search(users_by_cpf.root, cpf)
    if not result:
        return render_template("admin_page.html", user="admin",
                               users=CSVManager.get_users(),
                               msg="Usuário não existe!")

    # **Remover das B-Trees**
    node, idx = result
    line_number = node.values[idx]

    user_data = load_user_from_csv(line_number)
    if not user_data:
        return render_template("admin_page.html", user="admin",
                               users=CSVManager.get_users(),
                               msg="Erro ao localizar usuário.")

    users_by_cpf.remove(cpf)
    users_by_name.remove(user_data["name"])

    # Remover do CSV (não implementado ainda)
    msg = "Usuário removido das árvores (CSV ainda não é apagado)."

    return render_template("admin_page.html", user="admin", users=CSVManager.get_users(), msg=msg)


@login_bp.route("/change_password", methods=["POST"])
def change_password():
    cpf = request.form["cpf"]
    new_password = request.form["new_password"]

    result = users_by_cpf.search(users_by_cpf.root, cpf)
    if not result:
        return render_template("admin_page.html", user="admin",
                               users=CSVManager.get_users(),
                               msg="Usuário não existe!")

    node, idx = result
    line_number = node.values[idx]
    users = CSVManager.get_users()

    if 0 < line_number <= len(users):
        users[line_number - 1]["password"] = new_password
        CSVManager.save_all_users(users)

        msg = "Senha alterada com sucesso!"
    else:
        msg = "Erro ao alterar senha!"

    return render_template("admin_page.html", user="admin", users=users, msg=msg)


# -----------------------
# LOGOUT
# -----------------------
@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_bp.login"))

@login_bp.route("/search_user_by_name")
def search_user_by_name():
    nome = request.args.get("nome", "").strip()

    if not nome:
        return render_template("admin_dashboard.html", user="admin", users=get_all_users(), msg="Digite um nome para buscar.")

    # busca entre usuários
    result_user = users_tree.search(users_tree.root, nome)
    if result_user:
        return render_template("admin_dashboard.html", user="admin", users=[nome], msg=f"Usuário encontrado: {nome}")

    # busca entre administradores
    result_admin = admins_tree.search(admins_tree.root, nome)
    if result_admin:
        return render_template("admin_dashboard.html", user="admin", users=[nome], msg=f"Administrador encontrado: {nome}")

    return render_template("admin_dashboard.html", user="admin", users=get_all_users(), msg="Nenhum usuário encontrado com esse nome.")

@login_bp.route("/search_user_by_cpf")
def search_user_by_cpf():
    cpf = request.args.get("cpf", "").strip()

    if not cpf:
        return render_template("admin_dashboard.html", user="admin", users=get_all_users(), msg="Digite um CPF para buscar.")

    result_user = users_tree.search(users_tree.root, cpf)
    if result_user:
        return render_template("admin_dashboard.html", user="admin", users=[nome], msg=f"CPF encontrado: {cpf}")

    result_admin = admins_tree.search(admins_tree.root, cpf)
    if result_admins:
        return render_template("admin_dashboard.html", user="admin", users=[nome], msg=f"CPF encontrado: {cpf}")

    return render_template("admin_dashboard.html", user="admin", users=get_all_users(), msg="Nenhum usuário encontrado com esse CPF.")




# rota pra acessar a pagina do adms (so pra quem se logar)
@login_bp.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return "Acesso negado", 403
    return render_template("admin_dashboard.html")


# -----------------------
# REGISTRO RÁPIDO (usuário comum)
# -----------------------
@login_bp.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    cpf = request.form["cpf"]
    user = request.form["user"]
    password = request.form["password"]

    if users_by_cpf.search(users_by_cpf.root, cpf):
        msg = "CPF já registrado!"
    else:
        line = CSVManager.add_user([name, user, password, cpf, 0])
        users_by_cpf.insert(cpf, line)
        users_by_name.insert(name, line)
        msg = "Registro concluído!"

    return render_template("register_page.html", msg=msg)


@login_bp.route("/register_page")
def register_page():
    return render_template("register_page.html")
