
import os
import mysql.connector

from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# Secret key
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is not set")

# Security configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,  # True when deployed with HTTPS
    SESSION_COOKIE_SAMESITE="Lax"
)

# Enable CSRF protection
csrf = CSRFProtect(app)


# Home page - show products after login
@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()

    if db is None:
        return "Database connection failed!", 500

    try:
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        return render_template("products.html", products=products)

    except mysql.connector.Error:
        app.logger.exception("Database error on home page")
        return "Something went wrong. Please try again later.", 500

    finally:
        if db.is_connected():
            db.close()


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter email and password.")
            return redirect(url_for("login"))

        db = get_db_connection()

        if db is None:
            return "Database connection failed!", 500

        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            user = cursor.fetchone()

            cursor.close()

            if user and check_password_hash(
                user["password_hash"], password
            ):

                # Clear old session before login
                session.clear()

                session["user_id"] = user["user_id"]
                session["full_name"] = user["full_name"]

                return redirect(url_for("home"))

            flash("Invalid email or password.")

        except mysql.connector.Error:
            app.logger.exception("Database error during login")
            return "Something went wrong. Please try again later.", 500

        finally:
            if db.is_connected():
                db.close()

    return render_template("login.html")


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate fields
        if not all([full_name, email, phone, password, confirm_password]):
            flash("Please fill in all fields.")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect(url_for("signup"))

        # Hash password
        password_hash = generate_password_hash(password)

        db = get_db_connection()

        if db is None:
            return "Database connection failed!", 500

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

            flash("Registration successful! Please login.")
            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:
            db.rollback()
            flash("This email is already registered.")
            return redirect(url_for("signup"))

        except mysql.connector.Error:
            db.rollback()
            app.logger.exception("Database error during signup")
            return "Something went wrong. Please try again later.", 500

        finally:
            if db.is_connected():
                db.close()

    return render_template("signup.html")


# Logout
@app.route("/logout", methods=["POST"])
def logout():

    session.clear()
    return redirect(url_for("login"))


# Run application
if __name__ == "__main__":

    print("Starting YogaBite...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

