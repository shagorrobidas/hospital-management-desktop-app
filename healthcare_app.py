import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, date, timedelta

# Database setup (unchanged)
def create_db():
    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  password TEXT, 
                  role TEXT,
                  name TEXT,
                  specialization TEXT DEFAULT '',
                  contact TEXT DEFAULT '')''')
    c.execute('''CREATE TABLE IF NOT EXISTS schedules
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  doctor_id INTEGER, 
                  patient_id INTEGER, 
                  date TEXT, 
                  time TEXT,
                  status TEXT DEFAULT 'Available')''')
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  doctor_id INTEGER, 
                  patient_id INTEGER, 
                  prescription TEXT,
                  date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS patient_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  patient_id INTEGER, 
                  doctor_id INTEGER, 
                  record TEXT, 
                  date TEXT)''')
    conn.commit()
    conn.close()

create_db()

# User Registration (modified to include name)
def register_user():
    username = entry_username.get()
    password = entry_password.get()
    role = role_var.get()
    name = entry_name.get() if role != "Admin" else "Admin"

    if username and password and role:
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)", 
                  (username, password, role, name))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User registered successfully!")
        clear_register_fields()
    else:
        messagebox.showwarning("Input Error", "Please fill all fields")

def clear_register_fields():
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    role_var.set("Patient")

# Login Function (unchanged)
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
    dashboard.geometry("1000x700")

    # Common function to get user info
    def get_user_info(user_id):
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user

    user_info = get_user_info(user_id)

    # Display user info at top
    info_frame = ttk.LabelFrame(dashboard, text="User Information")
    info_frame.pack(fill='x', padx=10, pady=10)
    
    ttk.Label(info_frame, text=f"ID: {user_info[0]}").grid(row=0, column=0, sticky='w')
    ttk.Label(info_frame, text=f"Name: {user_info[4]}").grid(row=0, column=1, sticky='w')
    ttk.Label(info_frame, text=f"Role: {user_info[3]}").grid(row=0, column=2, sticky='w')
    if role == "Doctor":
        ttk.Label(info_frame, text=f"Specialization: {user_info[5]}").grid(row=1, column=0, sticky='w')
        ttk.Label(info_frame, text=f"Contact: {user_info[6]}").grid(row=1, column=1, sticky='w')

    if role == "Admin":
        admin_dashboard(dashboard, user_id)
    elif role == "Doctor":
        doctor_dashboard(dashboard, user_id)
    elif role == "Patient":
        patient_dashboard(dashboard, user_id)

def admin_dashboard(dashboard, user_id):
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill='both', expand=True)

    # Tab 1: Manage Users
    users_frame = ttk.Frame(notebook)
    notebook.add(users_frame, text='Manage Users')

    # Treeview for users
    user_columns = ('id', 'username', 'name', 'role', 'specialization', 'contact')
    user_tree = ttk.Treeview(users_frame, columns=user_columns, show='headings')
    user_tree.heading('id', text='ID')
    user_tree.heading('username', text='Username')
    user_tree.heading('name', text='Name')
    user_tree.heading('role', text='Role')
    user_tree.heading('specialization', text='Specialization')
    user_tree.heading('contact', text='Contact')
    user_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_users():
        for item in user_tree.get_children():
            user_tree.delete(item)
        
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute("SELECT id, username, name, role, specialization, contact FROM users")
        users = c.fetchall()
        conn.close()

        for user in users:
            user_tree.insert('', 'end', values=user)

    refresh_btn = ttk.Button(users_frame, text="Refresh", command=refresh_users)
    refresh_btn.pack(pady=10)

    # Tab 2: Manage Appointments
    appointments_frame = ttk.Frame(notebook)
    notebook.add(appointments_frame, text='Appointments')

    # Similar treeview for appointments
    # ... (implementation similar to users tab)

    # Tab 3: System Reports
    reports_frame = ttk.Frame(notebook)
    notebook.add(reports_frame, text='Reports')

    refresh_users()  # Load initial data

def doctor_dashboard(dashboard, user_id):
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill='both', expand=True)

    # Tab 1: My Schedule
    schedule_frame = ttk.Frame(notebook)
    notebook.add(schedule_frame, text='My Schedule')

    # Treeview for appointments
    columns = ('id', 'patient_id', 'patient_name', 'date', 'time', 'status')
    tree = ttk.Treeview(schedule_frame, columns=columns, show='headings')
    tree.heading('id', text='ID')
    tree.heading('patient_id', text='Patient ID')
    tree.heading('patient_name', text='Patient Name')
    tree.heading('date', text='Date')
    tree.heading('time', text='Time')
    tree.heading('status', text='Status')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_schedule():
        for item in tree.get_children():
            tree.delete(item)
        
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute('''SELECT s.id, s.patient_id, u.name, s.date, s.time, s.status 
                     FROM schedules s
                     LEFT JOIN users u ON s.patient_id = u.id
                     WHERE s.doctor_id=? ORDER BY s.date, s.time''', (user_id,))
        appointments = c.fetchall()
        conn.close()

        for appt in appointments:
            tree.insert('', 'end', values=appt)

    refresh_btn = ttk.Button(schedule_frame, text="Refresh Schedule", command=refresh_schedule)
    refresh_btn.pack(pady=10)

    # Tab 2: Add Availability
    availability_frame = ttk.Frame(notebook)
    notebook.add(availability_frame, text='Add Availability')

    # ... (same availability implementation as before)

    # Tab 3: Prescriptions
    prescriptions_frame = ttk.Frame(notebook)
    notebook.add(prescriptions_frame, text='Prescriptions')

    # Treeview for prescriptions
    presc_columns = ('id', 'patient_id', 'patient_name', 'date', 'prescription')
    presc_tree = ttk.Treeview(prescriptions_frame, columns=presc_columns, show='headings')
    presc_tree.heading('id', text='ID')
    presc_tree.heading('patient_id', text='Patient ID')
    presc_tree.heading('patient_name', text='Patient Name')
    presc_tree.heading('date', text='Date')
    presc_tree.heading('prescription', text='Prescription')
    presc_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_prescriptions():
        for item in presc_tree.get_children():
            presc_tree.delete(item)
        
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute('''SELECT p.id, p.patient_id, u.name, p.date, p.prescription 
                     FROM prescriptions p
                     LEFT JOIN users u ON p.patient_id = u.id
                     WHERE p.doctor_id=? ORDER BY p.date DESC''', (user_id,))
        prescriptions = c.fetchall()
        conn.close()

        for presc in prescriptions:
            presc_tree.insert('', 'end', values=presc)

    new_presc_btn = ttk.Button(prescriptions_frame, text="New Prescription", 
                              command=lambda: generate_prescription(user_id))
    new_presc_btn.pack(pady=5)
    
    refresh_presc_btn = ttk.Button(prescriptions_frame, text="Refresh", command=refresh_prescriptions)
    refresh_presc_btn.pack(pady=5)

    refresh_schedule()  # Load initial data
    refresh_prescriptions()

def patient_dashboard(dashboard, user_id):
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill='both', expand=True)

    # Tab 1: Book Appointment
    book_frame = ttk.Frame(notebook)
    notebook.add(book_frame, text='Book Appointment')

    # Doctor selection
    ttk.Label(book_frame, text="Select Doctor:").pack(pady=5)
    
    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT id, name, specialization FROM users WHERE role='Doctor'")
    doctors = c.fetchall()
    conn.close()
    
    doctor_var = tk.StringVar()
    doctor_combo = ttk.Combobox(book_frame, textvariable=doctor_var)
    doctor_combo['values'] = [f"{doc[0]} - {doc[1]} ({doc[2]})" for doc in doctors]
    doctor_combo.pack(pady=5)

    # Date and time selection
    ttk.Label(book_frame, text="Date:").pack(pady=5)
    date_entry = ttk.Entry(book_frame)
    date_entry.pack(pady=5)
    date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

    ttk.Label(book_frame, text="Time:").pack(pady=5)
    time_entry = ttk.Entry(book_frame)
    time_entry.pack(pady=5)

    def book_appointment():
        doctor_id = doctor_var.get().split(" - ")[0]
        appt_date = date_entry.get()
        appt_time = time_entry.get()

        if doctor_id and appt_date and appt_time:
            try:
                datetime.strptime(appt_date, "%Y-%m-%d")
                datetime.strptime(appt_time, "%H:%M")
                
                conn = sqlite3.connect('healthcare.db')
                c = conn.cursor()
                c.execute("INSERT INTO schedules (doctor_id, patient_id, date, time, status) VALUES (?, ?, ?, ?, ?)",
                          (doctor_id, user_id, appt_date, appt_time, "Booked"))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Appointment booked successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid date or time format (Use YYYY-MM-DD and HH:MM)")
        else:
            messagebox.showwarning("Error", "Please fill all fields")

    book_btn = ttk.Button(book_frame, text="Book Appointment", command=book_appointment)
    book_btn.pack(pady=10)

    # Tab 2: My Prescriptions
    prescriptions_frame = ttk.Frame(notebook)
    notebook.add(prescriptions_frame, text='My Prescriptions')

    # Treeview for prescriptions
    presc_columns = ('id', 'doctor_name', 'date', 'prescription')
    presc_tree = ttk.Treeview(prescriptions_frame, columns=presc_columns, show='headings')
    presc_tree.heading('id', text='ID')
    presc_tree.heading('doctor_name', text='Doctor')
    presc_tree.heading('date', text='Date')
    presc_tree.heading('prescription', text='Prescription')
    presc_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_prescriptions():
        for item in presc_tree.get_children():
            presc_tree.delete(item)
        
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute('''SELECT p.id, u.name, p.date, p.prescription 
                     FROM prescriptions p
                     LEFT JOIN users u ON p.doctor_id = u.id
                     WHERE p.patient_id=? ORDER BY p.date DESC''', (user_id,))
        prescriptions = c.fetchall()
        conn.close()

        for presc in prescriptions:
            presc_tree.insert('', 'end', values=presc)

    def download_selected_prescription():
        selected = presc_tree.selection()
        if selected:
            item = presc_tree.item(selected[0])
            presc_id = item['values'][0]
            
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()
            c.execute("SELECT prescription FROM prescriptions WHERE id=?", (presc_id,))
            prescription = c.fetchone()
            conn.close()
            
            if prescription:
                with open(f"prescription_{presc_id}.txt", "w") as f:
                    f.write(prescription[0])
                messagebox.showinfo("Success", f"Prescription {presc_id} downloaded!")
            else:
                messagebox.showerror("Error", "Prescription not found")

    refresh_btn = ttk.Button(prescriptions_frame, text="Refresh", command=refresh_prescriptions)
    refresh_btn.pack(pady=5)
    
    download_btn = ttk.Button(prescriptions_frame, text="Download Selected", 
                            command=download_selected_prescription)
    download_btn.pack(pady=5)

    refresh_prescriptions()  # Load initial data

# ... [Rest of the functions remain the same: generate_prescription, view_patient_history, etc.] ...

# Enhanced GUI Setup with name field
root = tk.Tk()
root.title("Healthcare Management System")

# Registration Frame with name field
frame_register = tk.LabelFrame(root, text="Register", padx=20, pady=20)
frame_register.pack(padx=20, pady=20)

tk.Label(frame_register, text="Username:").grid(row=0, column=0)
entry_username = tk.Entry(frame_register)
entry_username.grid(row=0, column=1)

tk.Label(frame_register, text="Password:").grid(row=1, column=0)
entry_password = tk.Entry(frame_register, show="*")
entry_password.grid(row=1, column=1)

tk.Label(frame_register, text="Full Name:").grid(row=2, column=0)
entry_name = tk.Entry(frame_register)
entry_name.grid(row=2, column=1)

tk.Label(frame_register, text="Role:").grid(row=3, column=0)
role_var = tk.StringVar(value="Patient")
tk.Radiobutton(
    frame_register,
    text="Patient",
    variable=role_var,
    value="Patient").grid(row=3, column=1)
tk.Radiobutton(
    frame_register,
    text="Doctor",
    variable=role_var,
    value="Doctor").grid(row=3, column=2)
tk.Radiobutton(
    frame_register,
    text="Admin",
    variable=role_var,
    value="Admin").grid(row=3, column=3)

tk.Button(frame_register, text="Register", command=register_user).grid(row=4, column=1)

# Login Frame (unchanged)
frame_login = tk.LabelFrame(root, text="Login", padx=20, pady=20)
frame_login.pack(padx=20, pady=20)

tk.Label(frame_login, text="Username:").grid(row=0, column=0)
entry_login_username = tk.Entry(frame_login)
entry_login_username.grid(row=0, column=1)

tk.Label(frame_login, text="Password:").grid(row=1, column=0)
entry_login_password = tk.Entry(frame_login, show="*")
entry_login_password.grid(row=1, column=1)

tk.Button(frame_login, text="Login", command=login).grid(row=2, column=1)

root.mainloop()