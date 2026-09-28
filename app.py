"""
Mini Secure Fintech Wallet - Phase 1: Basic Working Application
-----------------------------------------------------------------
This is the FUNCTIONAL version of the app, built BEFORE adding
security controls. We will deliberately add security weaknesses
here first, analyze them, then fix them one by one in later phases
(this matches the assignment's "before-and-after" requirement).

Run with:
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"  # NOTE: weak/hardcoded secret - flag this in your security analysis!

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "wallet.db")


# ---------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 1000.0
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# Routes
# ---------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username and password are required."
        else:
            conn = get_db()
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing:
                error = "Username already taken."
            else:
                # NOTE: storing password in PLAIN TEXT for now.
                # This is a deliberate weakness to fix in the security phase.
                conn.execute(
                    "INSERT INTO users (username, password, balance) VALUES (?, ?, ?)",
                    (username, password, 1000.0),
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            conn.close()

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()

    return render_template("dashboard.html", user=user)


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None
    success = None

    conn = get_db()

    if request.method == "POST":
        receiver_username = request.form.get("receiver", "").strip()
        amount_raw = request.form.get("amount", "")

        try:
            amount = float(amount_raw)
        except ValueError:
            amount = None

        sender = conn.execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        receiver = conn.execute(
            "SELECT * FROM users WHERE username = ?", (receiver_username,)
        ).fetchone()

        if not receiver:
            error = "Receiver not found."
        elif amount is None or amount <= 0:
            error = "Enter a valid amount."
        elif amount > sender["balance"]:
            error = "Insufficient balance."
        else:
            new_sender_balance = sender["balance"] - amount
            new_receiver_balance = receiver["balance"] + amount

            conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (new_sender_balance, sender["id"]),
            )
            conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (new_receiver_balance, receiver["id"]),
            )
            conn.execute(
                "INSERT INTO transactions (sender_id, receiver_id, amount, timestamp, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (sender["id"], receiver["id"], amount, datetime.now().isoformat(timespec="seconds"), "SUCCESS"),
            )
            conn.commit()
            success = f"Transferred Rs. {amount:.2f} to {receiver['username']}."

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()

    return render_template("transfer.html", user=user, error=error, success=success)


@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    rows = conn.execute(
        """
        SELECT t.id, su.username AS sender, ru.username AS receiver,
               t.amount, t.timestamp, t.status
        FROM transactions t
        JOIN users su ON t.sender_id = su.id
        JOIN users ru ON t.receiver_id = ru.id
        WHERE t.sender_id = ? OR t.receiver_id = ?
        ORDER BY t.timestamp DESC
        """,
        (session["user_id"], session["user_id"]),
    ).fetchall()
    conn.close()

    return render_template("history.html", transactions=rows, current_user_id=session["user_id"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
    init_db()
    app.run(debug=True)
