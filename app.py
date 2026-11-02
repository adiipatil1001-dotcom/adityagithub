from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from datetime import datetime
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'kolhapur_airlines_secret_key_2024'

# ─── Database Configuration ───────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',          # ← Set your MySQL password here
    'database': 'kolhapur_airlines',
    'autocommit': True
}

def get_db():
    """Return a fresh MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def generate_booking_ref():
    return 'KA' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) as cnt FROM flights WHERE status='scheduled'")
    flight_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM bookings WHERE booking_status='confirmed'")
    booking_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    user_count = cur.fetchone()['cnt']
    # Featured destinations
    cur.execute("""
        SELECT destination, MIN(economy_price) as from_price,
               COUNT(*) as flight_count
        FROM flights WHERE status='scheduled' AND available_seats > 0
        GROUP BY destination ORDER BY from_price ASC LIMIT 6
    """)
    destinations = cur.fetchall()
    cur.close(); db.close()
    return render_template('index.html',
                           flight_count=flight_count,
                           booking_count=booking_count,
                           user_count=user_count,
                           destinations=destinations)


@app.route('/flights')
def flights():
    db = get_db()
    cur = db.cursor(dictionary=True)

    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    date = request.args.get('date', '')

    query = "SELECT * FROM flights WHERE status='scheduled' AND available_seats > 0"
    params = []

    if origin:
        query += " AND origin LIKE %s"
        params.append(f'%{origin}%')

    if destination:
        query += " AND destination LIKE %s"
        params.append(f'%{destination}%')

    if date:
        query += " AND departure_date = %s"
        params.append(date)

    query += " ORDER BY departure_date, departure_time"

    cur.execute(query, params)
    flights_list = cur.fetchall()

    # FIX TIMEDELTA ERROR
    from datetime import timedelta
    for f in flights_list:
        if isinstance(f['departure_time'], timedelta):
            seconds = f['departure_time'].seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            f['departure_time'] = f"{hours:02d}:{minutes:02d}"

        if isinstance(f['arrival_time'], timedelta):
            seconds = f['arrival_time'].seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            f['arrival_time'] = f"{hours:02d}:{minutes:02d}"

    cur.execute("SELECT DISTINCT origin FROM flights ORDER BY origin")
    origins = [r['origin'] for r in cur.fetchall()]

    cur.execute("SELECT DISTINCT destination FROM flights ORDER BY destination")
    destinations = [r['destination'] for r in cur.fetchall()]

    cur.close()
    db.close()

    return render_template(
        'flights.html',
        flights=flights_list,
        origins=origins,
        destinations=destinations,
        selected_origin=origin,
        selected_destination=destination,
        selected_date=date
    )


    # Get distinct origins and destinations for dropdowns
    cur.execute("SELECT DISTINCT origin FROM flights ORDER BY origin")
    origins = [r['origin'] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT destination FROM flights ORDER BY destination")
    destinations = [r['destination'] for r in cur.fetchall()]
    cur.close(); db.close()
    return render_template('flights.html', flights=flights_list,
                           origins=origins, destinations=destinations,
                           selected_origin=origin, selected_destination=destination,
                           selected_date=date)


@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
def book(flight_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM flights WHERE id = %s", (flight_id,))
    flight = cur.fetchone()
    if not flight:
        flash('Flight not found.', 'danger')
        return redirect(url_for('flights'))

    if request.method == 'POST':
        passenger_name  = request.form['passenger_name'].strip()
        passenger_email = request.form['passenger_email'].strip()
        passenger_phone = request.form['passenger_phone'].strip()
        seat_class      = request.form['seat_class']
        num_passengers  = int(request.form.get('num_passengers', 1))

        price_map = {
            'economy':     float(flight['economy_price']),
            'business':    float(flight['business_price']),
            'first_class': float(flight['first_class_price']),
        }
        total_price = price_map.get(seat_class, float(flight['economy_price'])) * num_passengers

        if flight['available_seats'] < num_passengers:
            flash('Not enough seats available.', 'danger')
            return redirect(url_for('book', flight_id=flight_id))

        booking_ref = generate_booking_ref()
        # Ensure uniqueness
        while True:
            cur.execute("SELECT id FROM bookings WHERE booking_reference = %s", (booking_ref,))
            if not cur.fetchone():
                break
            booking_ref = generate_booking_ref()

        user_id = session.get('user_id')
        cur.execute("""
            INSERT INTO bookings
              (booking_reference, flight_id, user_id, passenger_name,
               passenger_email, passenger_phone, seat_class, num_passengers, total_price)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (booking_ref, flight_id, user_id, passenger_name,
              passenger_email, passenger_phone, seat_class, num_passengers, total_price))
        cur.execute("UPDATE flights SET available_seats = available_seats - %s WHERE id = %s",
                    (num_passengers, flight_id))
        cur.close(); db.close()
        return redirect(url_for('payment', ref=booking_ref))

    cur.close(); db.close()
    prefill = {}
    if 'user_id' in session:
        db2 = get_db()
        c2 = db2.cursor(dictionary=True)
        c2.execute("SELECT full_name, email, phone FROM users WHERE id=%s", (session['user_id'],))
        prefill = c2.fetchone() or {}
        c2.close(); db2.close()
    return render_template('book.html', flight=flight, prefill=prefill)

@app.route('/payment/<ref>')
def payment(ref):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT b.*, f.flight_number, f.origin, f.destination,
               f.departure_date, f.departure_time
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.booking_reference = %s
    """, (ref,))

    booking = cur.fetchone()

    cur.close()
    db.close()

    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('index'))

    return render_template('payment.html', booking=booking)


@app.route('/confirmation/<ref>')
def confirmation(ref):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, f.flight_number, f.origin, f.destination,
               f.departure_date, f.departure_time, f.arrival_time
        FROM bookings b JOIN flights f ON b.flight_id = f.id
        WHERE b.booking_reference = %s
    """, (ref,))
    booking = cur.fetchone()
    cur.close(); db.close()
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('index'))
    return render_template('confirmation.html', booking=booking)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        email     = request.form['email'].strip()
        phone     = request.form['phone'].strip()
        password  = request.form['password']
        confirm   = request.form['confirm_password']
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            cur.close(); db.close()
            return redirect(url_for('register'))
        pw_hash = generate_password_hash(password)
        cur.execute("INSERT INTO users (full_name, email, phone, password_hash) VALUES (%s,%s,%s,%s)",
                    (full_name, email, phone, pw_hash))
        cur.close(); db.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close(); db.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['full_name']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM admins WHERE username=%s", (username,))
        admin = cur.fetchone()
        cur.close(); db.close()
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id']   = admin['id']
            session['admin_name'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) as cnt FROM flights")
    total_flights = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM bookings WHERE booking_status='confirmed'")
    total_bookings = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    total_users = cur.fetchone()['cnt']
    cur.execute("SELECT COALESCE(SUM(total_price),0) as rev FROM bookings WHERE booking_status='confirmed'")
    total_revenue = cur.fetchone()['rev']
    # Recent bookings
    cur.execute("""
        SELECT b.booking_reference, b.passenger_name, b.total_price,
               b.booked_at, f.flight_number, f.origin, f.destination
        FROM bookings b JOIN flights f ON b.flight_id=f.id
        ORDER BY b.booked_at DESC LIMIT 8
    """)
    recent_bookings = cur.fetchall()
    # Bookings by class
    cur.execute("""
        SELECT seat_class, COUNT(*) as cnt, SUM(total_price) as revenue
        FROM bookings WHERE booking_status='confirmed'
        GROUP BY seat_class
    """)
    class_stats = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin/dashboard.html',
                           total_flights=total_flights,
                           total_bookings=total_bookings,
                           total_users=total_users,
                           total_revenue=total_revenue,
                           recent_bookings=recent_bookings,
                           class_stats=class_stats)


# ── Admin Flights ──────────────────────────────────────────────────────────────

@app.route('/admin/flights')
@admin_required
def admin_flights():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM flights ORDER BY departure_date, departure_time")
    flights_list = cur.fetchall()

    from datetime import timedelta

    # ✅ LOOP MUST BE INSIDE FUNCTION
    for f in flights_list:

        if isinstance(f['departure_time'], timedelta):
            seconds = f['departure_time'].seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            f['departure_time'] = f"{hours:02d}:{minutes:02d}"

        if isinstance(f['arrival_time'], timedelta):
            seconds = f['arrival_time'].seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            f['arrival_time'] = f"{hours:02d}:{minutes:02d}"

        # ✅ FIX DATE
        if f['departure_date']:
            try:
                f['departure_date'] = f['departure_date'].strftime('%d %b %Y')
            except:
                f['departure_date'] = str(f['departure_date'])

    cur.close()
    db.close()

    return render_template('admin/flights.html', flights=flights_list)


@app.route('/admin/flights/add', methods=['GET', 'POST'])
@admin_required
def admin_add_flight():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        try:
            seats = int(request.form['total_seats'])
            cur.execute("""
                INSERT INTO flights
                  (flight_number, origin, destination, departure_date, departure_time,
                   arrival_time, economy_price, business_price, first_class_price,
                   total_seats, available_seats, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                request.form['flight_number'], request.form['origin'],
                request.form['destination'], request.form['departure_date'],
                request.form['departure_time'], request.form['arrival_time'],
                request.form['economy_price'], request.form['business_price'],
                request.form['first_class_price'], seats, seats,
                request.form['status']
            ))
            flash('Flight added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            cur.close(); db.close()
        return redirect(url_for('admin_flights'))
    return render_template('admin/add_flight.html')


@app.route('/admin/flights/edit/<int:flight_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_flight(flight_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cur.execute("""
                UPDATE flights SET
                  flight_number=%s, origin=%s, destination=%s,
                  departure_date=%s, departure_time=%s, arrival_time=%s,
                  economy_price=%s, business_price=%s, first_class_price=%s,
                  total_seats=%s, available_seats=%s, status=%s
                WHERE id=%s
            """, (
                request.form['flight_number'], request.form['origin'],
                request.form['destination'], request.form['departure_date'],
                request.form['departure_time'], request.form['arrival_time'],
                request.form['economy_price'], request.form['business_price'],
                request.form['first_class_price'], request.form['total_seats'],
                request.form['available_seats'], request.form['status'], flight_id
            ))
            flash('Flight updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        cur.close(); db.close()
        return redirect(url_for('admin_flights'))
    cur.execute("SELECT * FROM flights WHERE id=%s", (flight_id,))
    flight = cur.fetchone()
    cur.close(); db.close()
    if not flight:
        flash('Flight not found.', 'danger')
        return redirect(url_for('admin_flights'))
    return render_template('admin/edit_flight.html', flight=flight)


@app.route('/admin/flights/delete/<int:flight_id>', methods=['POST'])
@admin_required
def admin_delete_flight(flight_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM flights WHERE id=%s", (flight_id,))
    cur.close(); db.close()
    flash('Flight deleted.', 'success')
    return redirect(url_for('admin_flights'))


# ── Admin Bookings ─────────────────────────────────────────────────────────────

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, f.flight_number, f.origin, f.destination,
               f.departure_date, f.departure_time
        FROM bookings b JOIN flights f ON b.flight_id=f.id
        ORDER BY b.booked_at DESC
    """)
    bookings = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin/bookings.html', bookings=bookings)


@app.route('/admin/bookings/cancel/<int:booking_id>', methods=['POST'])
@admin_required
def admin_cancel_booking(booking_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM bookings WHERE id=%s", (booking_id,))
    booking = cur.fetchone()
    if booking and booking['booking_status'] == 'confirmed':
        cur.execute("UPDATE bookings SET booking_status='cancelled' WHERE id=%s", (booking_id,))
        cur.execute("UPDATE flights SET available_seats=available_seats+%s WHERE id=%s",
                    (booking['num_passengers'], booking['flight_id']))
        flash('Booking cancelled.', 'success')
    cur.close(); db.close()
    return redirect(url_for('admin_bookings'))


# ── Admin Users ────────────────────────────────────────────────────────────────

@app.route('/admin/users')
@admin_required
def admin_users():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT u.*, COUNT(b.id) as booking_count
        FROM users u LEFT JOIN bookings b ON u.id=b.user_id
        GROUP BY u.id ORDER BY u.created_at DESC
    """)
    users = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin/users.html', users=users)


# ═══════════════════════════════════════════════════════════════════════════════
#  SETUP ROUTE  (run once to create admin account)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/setup')
def setup():
    """
    Visit http://localhost:5000/setup once to initialise the default admin.
    Then remove or protect this route.
    """
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id FROM admins WHERE username='admin'")
    existing = cur.fetchone()
    pw_hash = generate_password_hash('admin123')
    if existing:
        cur.execute("UPDATE admins SET password_hash=%s WHERE username='admin'", (pw_hash,))
        msg = 'Admin password reset to admin123.'
    else:
        cur.execute(
            "INSERT INTO admins (username, email, password_hash) VALUES (%s,%s,%s)",
            ('admin', 'admin@kolhapurairlines.com', pw_hash)
        )
        msg = 'Admin account created. Username: admin | Password: admin123'
    cur.close(); db.close()
    return f'<h2 style="font-family:sans-serif;padding:40px">{msg}</h2>'


if __name__ == '__main__':
    app.run(debug=True, port=5000)
