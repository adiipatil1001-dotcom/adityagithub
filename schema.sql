-- Kolhapur Airlines Database Schema
-- Run this file in MySQL to set up the database

CREATE DATABASE IF NOT EXISTS kolhapur_airlines;
USE kolhapur_airlines;

-- Flights Table
CREATE TABLE IF NOT EXISTS flights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL UNIQUE,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departure_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    economy_price DECIMAL(10,2) NOT NULL,
    business_price DECIMAL(10,2) NOT NULL,
    first_class_price DECIMAL(10,2) NOT NULL,
    total_seats INT NOT NULL DEFAULT 150,
    available_seats INT NOT NULL DEFAULT 150,
    status ENUM('scheduled', 'delayed', 'cancelled', 'completed') DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(20) NOT NULL UNIQUE,
    flight_id INT NOT NULL,
    user_id INT,
    passenger_name VARCHAR(100) NOT NULL,
    passenger_email VARCHAR(150) NOT NULL,
    passenger_phone VARCHAR(20) NOT NULL,
    seat_class ENUM('economy', 'business', 'first_class') NOT NULL DEFAULT 'economy',
    num_passengers INT NOT NULL DEFAULT 1,
    total_price DECIMAL(10,2) NOT NULL,
    booking_status ENUM('confirmed', 'cancelled', 'pending') DEFAULT 'confirmed',
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE
);

-- Admin Table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample Flights Data
INSERT INTO flights (flight_number, origin, destination, departure_date, departure_time, arrival_time, economy_price, business_price, first_class_price, total_seats, available_seats) VALUES
('KA-101', 'Mumbai', 'Kolhapur', '2026-04-01', '06:00:00', '07:15:00', 2500.00, 5500.00, 9500.00, 150, 148),
('KA-102', 'Kolhapur', 'Mumbai', '2026-04-01', '09:00:00', '10:15:00', 2500.00, 5500.00, 9500.00, 150, 145),
('KA-201', 'Pune', 'Kolhapur', '2026-04-02', '07:30:00', '08:30:00', 1800.00, 4200.00, 7800.00, 120, 120),
('KA-202', 'Kolhapur', 'Pune', '2026-04-02', '11:00:00', '12:00:00', 1800.00, 4200.00, 7800.00, 120, 118),
('KA-301', 'Delhi', 'Kolhapur', '2026-04-03', '05:45:00', '08:15:00', 4500.00, 9800.00, 16500.00, 180, 175),
('KA-302', 'Kolhapur', 'Delhi', '2026-04-03', '14:00:00', '16:30:00', 4500.00, 9800.00, 16500.00, 180, 172),
('KA-401', 'Bangalore', 'Kolhapur', '2026-04-04', '08:15:00', '09:45:00', 2200.00, 4900.00, 8500.00, 140, 139),
('KA-402', 'Kolhapur', 'Bangalore', '2026-04-04', '12:30:00', '14:00:00', 2200.00, 4900.00, 8500.00, 140, 136),
('KA-501', 'Hyderabad', 'Kolhapur', '2026-04-05', '10:00:00', '11:30:00', 2800.00, 6200.00, 10800.00, 160, 155),
('KA-502', 'Kolhapur', 'Hyderabad', '2026-04-05', '15:00:00', '16:30:00', 2800.00, 6200.00, 10800.00, 160, 152),
('KA-601', 'Goa', 'Kolhapur', '2026-04-06', '07:00:00', '07:45:00', 1500.00, 3500.00, 6500.00, 100, 98),
('KA-602', 'Kolhapur', 'Goa', '2026-04-06', '10:00:00', '10:45:00', 1500.00, 3500.00, 6500.00, 100, 97);

-- Default Admin (password: admin123)
INSERT INTO admins (username, email, password_hash) VALUES
('admin', 'admin@kolhapurairlines.com', 'pbkdf2:sha256:260000$placeholder$hash');

-- Note: Run update_admin_password.py to set the correct admin password hash
