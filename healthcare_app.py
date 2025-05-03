import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Database setup
def create_db():
    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS Hospital (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    email TEXT UNIQUE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Doctor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hospital_id INTEGER,
                    name TEXT NOT NULL,
                    specialization TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    email TEXT UNIQUE,
                    FOREIGN KEY (hospital_id) REFERENCES Hospital(id) ON DELETE CASCADE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Patient (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    email TEXT UNIQUE,
                    address TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Appointment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_id INTEGER,
                    patient_id INTEGER,
                    appointment_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Scheduled',
                    FOREIGN KEY (doctor_id) REFERENCES Doctor(id) ON DELETE CASCADE,
                    FOREIGN KEY (patient_id) REFERENCES Patient(id) ON DELETE CASCADE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Prescription (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_id INTEGER,
                    doctor_id INTEGER,
                    patient_id INTEGER,
                    date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (appointment_id) REFERENCES Appointment(id) ON DELETE CASCADE,
                    FOREIGN KEY (doctor_id) REFERENCES Doctor(id) ON DELETE CASCADE,
                    FOREIGN KEY (patient_id) REFERENCES Patient(id) ON DELETE CASCADE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Prescription_Medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prescription_id INTEGER,
                    medicine_name TEXT NOT NULL,
                    dosage TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    FOREIGN KEY (prescription_id) REFERENCES Prescription(id) ON DELETE CASCADE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Billing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_id INTEGER,
                    total_amount REAL NOT NULL,
                    payment_status TEXT NOT NULL DEFAULT 'Pending',
                    payment_date TEXT DEFAULT NULL,
                    FOREIGN KEY (appointment_id) REFERENCES Appointment(id) ON DELETE CASCADE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Staff (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hospital_id INTEGER,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    FOREIGN KEY (hospital_id) REFERENCES Hospital(id) ON DELETE CASCADE)''')
    
    conn.commit()
    conn.close()

create_db()

# User Registration
def register_user():
    username = entry_username.get()
    password = entry_password.get()
    role = role_var.get()

    if username and password and role:
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User registered successfully!")
    else:
        messagebox.showwarning("Input Error", "Please fill all fields")

# Login Function
def login():
    username = entry_login_username.get()
    password = entry_login_password.get()

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        role = user[3]
        open_role_dashboard(role, user[0])
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Role-Based Dashboards
def open_role_dashboard(role, user_id):
    dashboard = tk.Toplevel(root)
    dashboard.title(f"{role} Dashboard")

    if role == "Doctor":
        # Doctor Schedule
        tk.Label(dashboard, text="Your Schedule", font=("Arial", 14)).pack(pady=10)

        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Appointment WHERE doctor_id=?", (user_id,))
        appointments = c.fetchall()

        if appointments:
            for appointment in appointments:
                appointment_text = f"Date: {appointment[3]}, Patient ID: {appointment[2]}, Status: {appointment[4]}"
                tk.Label(dashboard, text=appointment_text).pack()
        else:
            tk.Label(dashboard, text="No appointments scheduled.").pack()

        conn.close()

        # Buttons for Doctor Features
        tk.Button(dashboard, text="Generate Prescription", command=lambda: generate_prescription(user_id)).pack(pady=10)
        tk.Button(dashboard, text="View Patient History", command=lambda: view_patient_history(user_id)).pack(pady=10)

    elif role == "Patient":
        # Book Appointment
        tk.Label(dashboard, text="Book Appointment", font=("Arial", 14)).pack(pady=10)

        tk.Label(dashboard, text="Doctor ID:").pack()
        doctor_id_entry = tk.Entry(dashboard)
        doctor_id_entry.pack()

        tk.Label(dashboard, text="Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(dashboard)
        date_entry.pack()

        tk.Label(dashboard, text="Time (HH:MM):").pack()
        time_entry = tk.Entry(dashboard)
        time_entry.pack()

        def book_appointment():
            doctor_id = doctor_id_entry.get()
            date = date_entry.get()
            time = time_entry.get()

            if doctor_id and date and time:
                conn = sqlite3.connect('healthcare.db')
                c = conn.cursor()
                c.execute("INSERT INTO Appointment (doctor_id, patient_id, appointment_date, status) VALUES (?, ?, ?, ?)",
                          (doctor_id, user_id, f"{date} {time}", 'Scheduled'))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Appointment booked!")
            else:
                messagebox.showwarning("Input Error", "Please fill all fields")

        tk.Button(dashboard, text="Book Appointment", command=book_appointment).pack(pady=10)

        # Download Prescription
        tk.Button(dashboard, text="Download Prescription", command=lambda: download_prescription(user_id)).pack(pady=10)

    elif role == "Admin":
        # Admin Panel
        tk.Label(dashboard, text="Admin Panel", font=("Arial", 14)).pack(pady=10)

        # View All Users
        tk.Button(dashboard, text="View All Users", command=view_all_users).pack(pady=10)

        # View All Appointments
        tk.Button(dashboard, text="View All Appointments", command=view_all_appointments).pack(pady=10)

        # View All Prescriptions
        tk.Button(dashboard, text="View All Prescriptions", command=view_all_prescriptions).pack(pady=10)

# Prescription Functions
def generate_prescription(doctor_id):
    prescription_window = tk.Toplevel(root)
    prescription_window.title("Generate Prescription")

    tk.Label(prescription_window, text="Patient ID:").pack()
    patient_id_entry = tk.Entry(prescription_window)
    patient_id_entry.pack()

    tk.Label(prescription_window, text="Prescription:").pack()
    prescription_entry = tk.Text(prescription_window)
    prescription_entry.pack()

    def save_prescription():
        patient_id = patient_id_entry.get()
        prescription = prescription_entry.get("1.0", tk.END)

        if patient_id and prescription:
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()
            c.execute("INSERT INTO Prescription (doctor_id, patient_id, notes) VALUES (?, ?, ?)",
                      (doctor_id, patient_id, prescription))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Prescription saved!")
            prescription_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields")

    tk.Button(prescription_window, text="Save", command=save_prescription).pack()

def download_prescription(patient_id):
    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Prescription WHERE patient_id=?", (patient_id,))
    prescriptions = c.fetchall()
    conn.close()

    if prescriptions:
        for prescription in prescriptions:
            with open(f"prescription_{prescription[0]}.txt", "w") as file:
                file.write(prescription[5])
        messagebox.showinfo("Success", "Prescriptions downloaded!")
    else:
        messagebox.showwarning("No Data", "No prescriptions found")

# Patient History Functions
def view_patient_history(doctor_id):
    history_window = tk.Toplevel(root)
    history_window.title("Patient History")

    tk.Label(history_window, text="Patient ID:").pack()
    patient_id_entry = tk.Entry(history_window)
    patient_id_entry.pack()

    def fetch_history():
        patient_id = patient_id_entry.get()
        if patient_id:
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()
            c.execute("SELECT * FROM Prescription WHERE patient_id=?", (patient_id,))
            history = c.fetchall()
            conn.close()

            if history:
                for record in history:
                    record_text = f"Date: {record[4]}, Doctor ID: {record[2]}, Notes: {record[5]}"
                    tk.Label(history_window, text=record_text).pack()
            else:
                tk.Label(history_window, text="No history found.").pack()
        else:
            messagebox.showwarning("Input Error", "Please enter a patient ID")

    tk.Button(history_window, text="Fetch History", command=fetch_history).pack()

# Admin Functions
def view_all_users():
    users_window = tk.Toplevel(root)
    users_window.title("All Users")

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    for user in users:
        user_text = f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}"
        tk.Label(users_window, text=user_text).pack()

def view_all_appointments():
    appointments_window = tk.Toplevel(root)
    appointments_window.title("All Appointments")

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Appointment")
    appointments = c.fetchall()
    conn.close()

    for appointment in appointments:
        appointment_text = f"Doctor ID: {appointment[1]}, Patient ID: {appointment[2]}, Date: {appointment[3]}, Status: {appointment[4]}"
        tk.Label(appointments_window, text=appointment_text).pack()

def view_all_prescriptions():
    prescriptions_window = tk.Toplevel(root)
    prescriptions_window.title("All Prescriptions")

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Prescription")
    prescriptions = c.fetchall()
    conn.close()

    for prescription in prescriptions:
        prescription_text = f"Doctor ID: {prescription[2]}, Patient ID: {prescription[3]}, Notes: {prescription[5]}"
        tk.Label(prescriptions_window, text=prescription_text).pack()

# GUI Setup
root = tk.Tk()
root.title("Healthcare Management System")

# Registration Frame
frame_register = tk.LabelFrame(root, text="Register", padx=10, pady=10)
frame_register.pack(padx=10, pady=10)

tk.Label(frame_register, text="Username:").grid(row=0, column=0)
entry_username = tk.Entry(frame_register)
entry_username.grid(row=0, column=1)

tk.Label(frame_register, text="Password:").grid(row=1, column=0)
entry_password = tk.Entry(frame_register, show="*")
entry_password.grid(row=1, column=1)

tk.Label(frame_register, text="Role:").grid(row=2, column=0)
role_var = tk.StringVar(value="Patient")
tk.Radiobutton(frame_register, text="Patient", variable=role_var, value="Patient").grid(row=2, column=1)
tk.Radiobutton(frame_register, text="Doctor", variable=role_var, value="Doctor").grid(row=2, column=2)
tk.Radiobutton(frame_register, text="Admin", variable=role_var, value="Admin").grid(row=2, column=3)

tk.Button(frame_register, text="Register", command=register_user).grid(row=3, column=1)

# Login Frame
frame_login = tk.LabelFrame(root, text="Login", padx=10, pady=10)
frame_login.pack(padx=10, pady=10)

tk.Label(frame_login, text="Username:").grid(row=0, column=0)
entry_login_username = tk.Entry(frame_login)
entry_login_username.grid(row=0, column=1)

tk.Label(frame_login, text="Password:").grid(row=1, column=0)
entry_login_password = tk.Entry(frame_login, show="*")
entry_login_password.grid(row=1, column=1)

tk.Button(frame_login, text="Login", command=login).grid(row=2, column=1)

# Start the GUI event loop
root.mainloop()