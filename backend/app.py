from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db, init_db
from datetime import datetime
import random, uuid

app = Flask(__name__)
CORS(app)

# INIT DB
init_db()

# ------------------------
# CONFIG (TEMP ADMIN LOGIN)
# ------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ------------------------
# HELPERS
# ------------------------
def generate_booking_id():
    return "BK" + str(random.randint(100000, 999999))

# ------------------------
# HOME
# ------------------------
@app.route("/")
def home():
    return jsonify({
        "status": "OK",
        "message": "QR Resto Resort backend running"
    })

# ------------------------
# ADMIN LOGIN ✅ (NEW)
# ------------------------
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = str(uuid.uuid4())
        return jsonify({
            "message": "Login successful",
            "token": token
        })

    return jsonify({"error": "Invalid credentials"}), 401

# ------------------------
# CREATE BOOKING
# ------------------------
@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.json

    service = data.get("service")
    details = data.get("details")
    amount = data.get("amount")

    if not service or not details or not amount:
        return jsonify({"error": "Missing fields"}), 400

    booking_id = generate_booking_id()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings
        (booking_id, service, details, amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        booking_id,
        service,
        details,
        amount,
        "CONFIRMED",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Booking created",
        "booking_id": booking_id
    }), 201

# ------------------------
# LIST BOOKINGS
# ------------------------
@app.route("/api/bookings", methods=["GET"])
def list_bookings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# ------------------------
# GET SINGLE BOOKING
# ------------------------
@app.route("/api/bookings/<booking_id>", methods=["GET"])
def get_booking(booking_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT booking_id, service, details, amount, status, created_at
        FROM bookings WHERE booking_id=?
    """, (booking_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify(dict(row))

# ------------------------
# UPDATE STATUS
# ------------------------
@app.route("/api/bookings/<booking_id>/status", methods=["PUT"])
def update_booking_status(booking_id):
    data = request.json
    new_status = data.get("status")

    if new_status not in ["CONFIRMED", "PAID", "CANCELLED"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE bookings SET status=? WHERE booking_id=?",
        (new_status, booking_id)
    )

    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "Booking not found"}), 404

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Status updated",
        "booking_id": booking_id,
        "status": new_status
    })

# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
