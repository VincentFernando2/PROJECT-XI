from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from db_config import get_db_connection
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user["id"], user["username"])
    return None

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            login_user(User(user["id"], user["username"]))
            flash("Login berhasil!")
            return redirect(url_for("index"))
        else:
            flash("Login gagal. Periksa username dan password.")
    
    return render_template("login.html")

# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.")
    return redirect(url_for("login"))

# Home Page - Menu Management
@app.route("/")
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    menus = cursor.fetchall()
    conn.close()
    return render_template("index.html", menus=menus)

# Add Menu Route
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_menu():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO menu (name, price, description) VALUES (%s, %s, %s)", (name, price, description))
        conn.commit()
        conn.close()
        
        flash("Menu berhasil ditambahkan!")
        return redirect(url_for("index"))
    
    return render_template("add_menu.html")

# Edit Menu Route
@app.route("/edit/<int:menu_id>", methods=["GET", "POST"])
@login_required
def edit_menu(menu_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        
        cursor.execute("UPDATE menu SET name=%s, price=%s, description=%s WHERE id=%s", (name, price, description, menu_id))
        conn.commit()
        conn.close()
        
        flash("Menu berhasil diperbarui!")
        return redirect(url_for("index"))
    
    cursor.execute("SELECT * FROM menu WHERE id=%s", (menu_id,))
    menu = cursor.fetchone()
    conn.close()
    return render_template("edit_menu.html", menu=menu)

# Delete Menu Route
@app.route("/delete/<int:menu_id>", methods=["POST"])
@login_required
def delete_menu(menu_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id=%s", (menu_id,))
    conn.commit()
    conn.close()
    
    flash("Menu berhasil dihapus!")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
