# ✈️ Kolhapur Airlines — Full-Stack Booking System

A complete airline booking web application built with **Python Flask** and **MySQL**.

---

## 🚀 Quick Start (5 Steps)

### Step 1 — Install Python Dependencies
```bash
pip install flask mysql-connector-python werkzeug
```

### Step 2 — Set Up MySQL Database
Open MySQL (via phpMyAdmin, MySQL Workbench, or terminal) and run the schema file:
```sql
SOURCE schema.sql;
-- OR copy-paste the contents of schema.sql into your MySQL client
```

### Step 3 — Configure Database Connection
Open `app.py` and update the `DB_CONFIG` section at the top:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',  # ← change this
    'database': 'kolhapur_airlines',
}
```

### Step 4 — Run the App
```bash
python app.py
```

### Step 5 — Set Up Admin Account
Visit this URL once in your browser to create the admin account:
```
http://localhost:5000/setup
```
This creates: **Username: admin | Password: admin123**

---

## 🌐 Application URLs

| Page | URL |
|------|-----|
| Homepage | http://localhost:5000/ |
| Flights | http://localhost:5000/flights |
| Register | http://localhost:5000/register |
| Login | http://localhost:5000/login |
| **Admin Login** | http://localhost:5000/admin/login |
| Admin Dashboard | http://localhost:5000/admin/dashboard |
| Admin Flights | http://localhost:5000/admin/flights |
| Admin Bookings | http://localhost:5000/admin/bookings |
| Admin Users | http://localhost:5000/admin/users |

---

## 📁 Project Structure

```
kolhapur_airlines/
│
├── app.py                    # Main Flask application
├── schema.sql                # MySQL database schema + sample data
├── requirements.txt          # Python dependencies
│
└── templates/
    ├── base.html             # Base template (navbar, footer)
    ├── index.html            # Homepage with hero + search
    ├── flights.html          # Flight listing with filters
    ├── book.html             # Booking form
    ├── confirmation.html     # Booking confirmation + ticket
    ├── login.html            # User login
    ├── register.html         # User registration
    ├── about.html            # About page
    ├── contact.html          # Contact page
    │
    └── admin/
        ├── base_admin.html   # Admin layout with sidebar
        ├── login.html        # Admin login
        ├── dashboard.html    # Stats + recent bookings
        ├── flights.html      # Flight management table
        ├── add_flight.html   # Add new flight form
        ├── edit_flight.html  # Edit flight form
        ├── bookings.html     # All bookings table
        └── users.html        # Registered users table
```

---

## 🗄️ Database Tables

| Table | Description |
|-------|-------------|
| `flights` | Flight routes, times, prices, seat availability |
| `bookings` | Passenger bookings with reference numbers |
| `users` | Registered user accounts |
| `admins` | Admin login accounts |

---

## ✨ Features

### Public Site
- **Homepage** — Hero section, destination cards, quick search form, statistics
- **Flights Page** — Filter by origin, destination, and date
- **Booking System** — Seat class selection, dynamic price calculator, booking reference generation
- **Confirmation Page** — Printable boarding pass with full booking details
- **User Auth** — Register, login, and logout

### Admin Panel
- **Dashboard** — Live stats (flights, bookings, users, revenue) + recent activity
- **Flight Management** — Add, edit, delete flights; manage seat availability and status
- **Booking Management** — View all bookings, cancel bookings (auto-releases seats)
- **User Management** — View all registered users and their booking counts

---

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL (via mysql-connector-python)
- **Frontend**: HTML5, Bootstrap 5, Vanilla JS
- **Fonts**: Playfair Display + DM Sans (Google Fonts)
- **Icons**: Bootstrap Icons

---

## 🔐 Default Admin Credentials

After running `/setup`:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ Change these in production!

---

## 💡 Sample Flights Included

The schema includes 12 sample flights across routes:
- Kolhapur ↔ Mumbai (KA-101/102)
- Kolhapur ↔ Pune (KA-201/202)
- Kolhapur ↔ Delhi (KA-301/302)
- Kolhapur ↔ Bangalore (KA-401/402)
- Kolhapur ↔ Hyderabad (KA-501/502)
- Kolhapur ↔ Goa (KA-601/602)
