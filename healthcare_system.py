import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime


# Database setup
def create_db():
    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS schedules
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, doctor_id INTEGER, patient_id INTEGER, date TEXT, time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, doctor_id INTEGER, patient_id INTEGER, prescription TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS patient_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, doctor_id INTEGER, record TEXT, date TEXT)''')
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
        c.execute("SELECT * FROM schedules WHERE doctor_id=?", (user_id,))
        schedules = c.fetchall()

        if schedules:
            for schedule in schedules:
                schedule_text = f"Date: {schedule[3]}, Time: {schedule[4]}, Patient ID: {schedule[2]}"
                tk.Label(dashboard, text=schedule_text).pack()
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
                c.execute("INSERT INTO schedules (doctor_id, patient_id, date, time) VALUES (?, ?, ?, ?)",
                          (doctor_id, user_id, date, time))
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

        # View All Schedules
        tk.Button(dashboard, text="View All Schedules", command=view_all_schedules).pack(pady=10)

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
            c.execute("INSERT INTO prescriptions (doctor_id, patient_id, prescription) VALUES (?, ?, ?)",
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
    c.execute("SELECT * FROM prescriptions WHERE patient_id=?", (patient_id,))
    prescriptions = c.fetchall()
    conn.close()

    if prescriptions:
        for prescription in prescriptions:
            with open(f"prescription_{prescription[0]}.txt", "w") as file:
                file.write(prescription[3])
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
            c.execute("SELECT * FROM patient_history WHERE patient_id=?", (patient_id,))
            history = c.fetchall()
            conn.close()

            if history:
                for record in history:
                    record_text = f"Date: {record[4]}, Doctor ID: {record[2]}, Record: {record[3]}"
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

def view_all_schedules():
    schedules_window = tk.Toplevel(root)
    schedules_window.title("All Schedules")

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT * FROM schedules")
    schedules = c.fetchall()
    conn.close()

    for schedule in schedules:
        schedule_text = f"Doctor ID: {schedule[1]}, Patient ID: {schedule[2]}, Date: {schedule[3]}, Time: {schedule[4]}"
        tk.Label(schedules_window, text=schedule_text).pack()


def view_all_prescriptions():
    prescriptions_window = tk.Toplevel(root)
    prescriptions_window.title("All Prescriptions")

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT * FROM prescriptions")
    prescriptions = c.fetchall()
    conn.close()

    for prescription in prescriptions:
        prescription_text = f"Doctor ID: {prescription[1]}, Patient ID: {prescription[2]}, Prescription: {prescription[3]}"
        tk.Label(prescriptions_window, text=prescription_text).pack()


# GUI Setup
root = tk.Tk()
root.title("Healthcare Management System")

# Registration Frame
frame_register = tk.LabelFrame(root, text="Register", padx=20, pady=20)
frame_register.pack(padx=20, pady=20)

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
frame_login = tk.LabelFrame(root, text="Login", padx=20, pady=20)
frame_login.pack(padx=20, pady=20)

tk.Label(frame_login, text="Username:").grid(row=0, column=0)
entry_login_username = tk.Entry(frame_login)
entry_login_username.grid(row=0, column=1)

tk.Label(frame_login, text="Password:").grid(row=1, column=0)
entry_login_password = tk.Entry(frame_login, show="*")
entry_login_password.grid(row=1, column=1)

tk.Button(frame_login, text="Login", command=login).grid(row=2, column=1)

# Start the GUI event loop
root.mainloop()