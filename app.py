import os 
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is not set")

# Home page - show products after login
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()

    if db is None:
        return "Database connection failed!"

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template("products.html", products=products)

    except Exception as error:
        db.close()
        return f"Error: {error}", 500


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        db = get_db_connection()

        if db is None:
            return "Database connection failed!"

        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            user = cursor.fetchone()
            cursor.close()
            db.close()

            if user and check_password_hash(
                user["password_hash"], password
            ):
                session["user_id"] = user["user_id"]
                session["full_name"] = user["full_name"]

                return redirect(url_for("home"))

            flash("Invalid email or password.")

        except Exception as error:
            db.close()
            return f"Error: {error}", 500

    return render_template("login.html")


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not all([full_name, email, phone, password]):
            flash("Please fill in all fields.")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect(url_for("signup"))

        password_hash = generate_password_hash(password)

        db = get_db_connection()

        if db is None:
            return "Database connection failed!"

        try:
            cursor = db.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (full_name, email, phone, password_hash)
                VALUES (%s, %s, %s, %s)
                """,
                (full_name, email, phone, password_hash)
            )

            db.commit()
            cursor.close()
            db.close()

            flash("Registration successful! Please login.")
            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:
            db.close()
            flash("This email is already registered.")
            return redirect(url_for("signup"))

        except Exception as error:
            db.rollback()
            db.close()
            return f"Error: {error}", 500

    return render_template("signup.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    print("Starting YogaBite...")
    app.run(debug=True)



