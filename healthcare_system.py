import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, date, timedelta

# Database setup
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

# Prescription Functions
def generate_prescription(doctor_id):
    prescription_window = tk.Toplevel(root)
    prescription_window.title("Generate Prescription")
    prescription_window.geometry("500x400")

    tk.Label(prescription_window, text="Patient ID:").pack(pady=5)
    patient_id_entry = tk.Entry(prescription_window)
    patient_id_entry.pack(pady=5)

    tk.Label(prescription_window, text="Prescription:").pack(pady=5)
    prescription_entry = tk.Text(prescription_window, height=15)
    prescription_entry.pack(pady=5, fill='both', expand=True)

    def save_prescription():
        patient_id = patient_id_entry.get()
        prescription = prescription_entry.get("1.0", tk.END)
        today = date.today().strftime("%Y-%m-%d")

        if patient_id and prescription.strip():
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()
            c.execute("INSERT INTO prescriptions (doctor_id, patient_id, prescription, date) VALUES (?, ?, ?, ?)",
                      (doctor_id, patient_id, prescription.strip(), today))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Prescription saved!")
            prescription_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields")

    save_btn = ttk.Button(prescription_window, text="Save Prescription", command=save_prescription)
    save_btn.pack(pady=10)

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
    history_window.geometry("600x400")

    tk.Label(history_window, text="Patient ID:").pack(pady=5)
    patient_id_entry = tk.Entry(history_window)
    patient_id_entry.pack(pady=5)

    history_frame = ttk.Frame(history_window)
    history_frame.pack(fill='both', expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(history_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    history_text = tk.Text(history_frame, yscrollcommand=scrollbar.set)
    history_text.pack(fill='both', expand=True)

    scrollbar.config(command=history_text.yview)

    def fetch_history():
        patient_id = patient_id_entry.get()
        if patient_id:
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()
            c.execute("SELECT * FROM patient_history WHERE patient_id=?", (patient_id,))
            history = c.fetchall()
            conn.close()

            history_text.delete(1.0, tk.END)
            if history:
                for record in history:
                    record_text = f"Date: {record[4]}\nDoctor ID: {record[2]}\nRecord: {record[3]}\n{'='*50}\n"
                    history_text.insert(tk.END, record_text)
            else:
                history_text.insert(tk.END, "No history found for this patient.")
        else:
            messagebox.showwarning("Input Error", "Please enter a patient ID")

    fetch_btn = ttk.Button(history_window, text="Fetch History", command=fetch_history)
    fetch_btn.pack(pady=10)

# Admin Functions
def view_all_users():
    users_window = tk.Toplevel(root)
    users_window.title("All Users")
    users_window.geometry("800x400")

    tree = ttk.Treeview(users_window, columns=('id', 'username', 'name', 'role', 'specialization', 'contact'), show='headings')
    tree.heading('id', text='ID')
    tree.heading('username', text='Username')
    tree.heading('name', text='Name')
    tree.heading('role', text='Role')
    tree.heading('specialization', text='Specialization')
    tree.heading('contact', text='Contact')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT id, username, name, role, specialization, contact FROM users")
    users = c.fetchall()
    conn.close()

    for user in users:
        tree.insert('', 'end', values=user)

def view_all_schedules():
    schedules_window = tk.Toplevel(root)
    schedules_window.title("All Schedules")
    schedules_window.geometry("800x400")

    tree = ttk.Treeview(schedules_window, columns=('id', 'doctor_id', 'patient_id', 'date', 'time', 'status'), show='headings')
    tree.heading('id', text='ID')
    tree.heading('doctor_id', text='Doctor ID')
    tree.heading('patient_id', text='Patient ID')
    tree.heading('date', text='Date')
    tree.heading('time', text='Time')
    tree.heading('status', text='Status')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT id, doctor_id, patient_id, date, time, status FROM schedules")
    schedules = c.fetchall()
    conn.close()

    for schedule in schedules:
        tree.insert('', 'end', values=schedule)

def view_all_prescriptions():
    prescriptions_window = tk.Toplevel(root)
    prescriptions_window.title("All Prescriptions")
    prescriptions_window.geometry("800x400")

    tree = ttk.Treeview(prescriptions_window, columns=('id', 'doctor_id', 'patient_id', 'date'), show='headings')
    tree.heading('id', text='ID')
    tree.heading('doctor_id', text='Doctor ID')
    tree.heading('patient_id', text='Patient ID')
    tree.heading('date', text='Date')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(prescriptions_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_frame = ttk.Frame(prescriptions_window)
    text_frame.pack(fill='both', expand=True)

    prescription_text = tk.Text(text_frame, yscrollcommand=scrollbar.set)
    prescription_text.pack(fill='both', expand=True)

    scrollbar.config(command=prescription_text.yview)

    def show_prescription(event):
        selected_item = tree.focus()
        if selected_item:
            item = tree.item(selected_item)
            prescription_id = item['values'][0]
            
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()
            c.execute("SELECT prescription FROM prescriptions WHERE id=?", (prescription_id,))
            prescription = c.fetchone()
            conn.close()
            
            prescription_text.delete(1.0, tk.END)
            if prescription:
                prescription_text.insert(tk.END, prescription[0])

    tree.bind('<<TreeviewSelect>>', show_prescription)

    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()
    c.execute("SELECT id, doctor_id, patient_id, date FROM prescriptions")
    prescriptions = c.fetchall()
    conn.close()

    for prescription in prescriptions:
        tree.insert('', 'end', values=prescription)

# User Registration
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
    dashboard.geometry("1000x700")

    def get_user_info(user_id):
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user

    user_info = get_user_info(user_id)

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

    appt_columns = ('id', 'doctor_id', 'doctor_name', 'patient_id', 'patient_name', 'date', 'time', 'status')
    appt_tree = ttk.Treeview(appointments_frame, columns=appt_columns, show='headings')
    appt_tree.heading('id', text='ID')
    appt_tree.heading('doctor_id', text='Doctor ID')
    appt_tree.heading('doctor_name', text='Doctor Name')
    appt_tree.heading('patient_id', text='Patient ID')
    appt_tree.heading('patient_name', text='Patient Name')
    appt_tree.heading('date', text='Date')
    appt_tree.heading('time', text='Time')
    appt_tree.heading('status', text='Status')
    appt_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_appointments():
        for item in appt_tree.get_children():
            appt_tree.delete(item)
        
        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()
        c.execute('''SELECT s.id, s.doctor_id, d.name, s.patient_id, p.name, s.date, s.time, s.status 
                     FROM schedules s
                     LEFT JOIN users d ON s.doctor_id = d.id
                     LEFT JOIN users p ON s.patient_id = p.id''')
        appointments = c.fetchall()
        conn.close()

        for appt in appointments:
            appt_tree.insert('', 'end', values=appt)

    refresh_appt_btn = ttk.Button(appointments_frame, text="Refresh", command=refresh_appointments)
    refresh_appt_btn.pack(pady=10)

    # Tab 3: System Reports
    reports_frame = ttk.Frame(notebook)
    notebook.add(reports_frame, text='Reports')

    refresh_users()
    refresh_appointments()

def doctor_dashboard(dashboard, user_id):
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill='both', expand=True)

    # Tab 1: My Schedule
    schedule_frame = ttk.Frame(notebook)
    notebook.add(schedule_frame, text='My Schedule')

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

    ttk.Label(availability_frame, text="Date:").pack(pady=5)
    date_entry = ttk.Entry(availability_frame)
    date_entry.pack(pady=5)
    date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

    time_frame = ttk.Frame(availability_frame)
    time_frame.pack(pady=10)

    ttk.Label(time_frame, text="Start Time:").grid(row=0, column=0, padx=5)
    start_hour = ttk.Combobox(time_frame, values=[f"{h:02d}" for h in range(9, 18)], width=3)
    start_hour.grid(row=0, column=1, padx=5)
    start_hour.set("09")
    ttk.Label(time_frame, text=":").grid(row=0, column=2)
    start_min = ttk.Combobox(time_frame, values=["00", "15", "30", "45"], width=3)
    start_min.grid(row=0, column=3, padx=5)
    start_min.set("00")

    ttk.Label(time_frame, text="End Time:").grid(row=1, column=0, padx=5)
    end_hour = ttk.Combobox(time_frame, values=[f"{h:02d}" for h in range(9, 18)], width=3)
    end_hour.grid(row=1, column=1, padx=5)
    end_hour.set("17")
    ttk.Label(time_frame, text=":").grid(row=1, column=2)
    end_min = ttk.Combobox(time_frame, values=["00", "15", "30", "45"], width=3)
    end_min.grid(row=1, column=3, padx=5)
    end_min.set("00")

    ttk.Label(availability_frame, text="Appointment Duration (minutes):").pack(pady=5)
    duration = ttk.Combobox(availability_frame, values=[15, 30, 45, 60], width=5)
    duration.pack(pady=5)
    duration.set(30)

    def add_availability():
        try:
            appt_date = date_entry.get()
            start_time = f"{start_hour.get()}:{start_min.get()}"
            end_time = f"{end_hour.get()}:{end_min.get()}"
            duration_val = int(duration.get())
            
            datetime.strptime(appt_date, "%Y-%m-%d")
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()
            
            current_time = datetime.strptime(start_time, "%H:%M")
            end_time_dt = datetime.strptime(end_time, "%H:%M")
            
            while current_time + timedelta(minutes=duration_val) <= end_time_dt:
                slot_end = current_time + timedelta(minutes=duration_val)
                
                c.execute("SELECT id FROM schedules WHERE doctor_id=? AND date=? AND time=?",
                         (user_id, appt_date, current_time.strftime("%H:%M")))
                if not c.fetchone():
                    c.execute("INSERT INTO schedules (doctor_id, date, time) VALUES (?, ?, ?)",
                             (user_id, appt_date, current_time.strftime("%H:%M")))
                
                current_time = slot_end
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Availability slots added!")
            refresh_schedule()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    add_btn = ttk.Button(availability_frame, text="Add Availability Slots", command=add_availability)
    add_btn.pack(pady=20)

    # Tab 3: Prescriptions
    prescriptions_frame = ttk.Frame(notebook)
    notebook.add(prescriptions_frame, text='Prescriptions')

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

    refresh_schedule()
    refresh_prescriptions()

def patient_dashboard(dashboard, user_id):
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill='both', expand=True)

    # Tab 1: Book Appointment
    book_frame = ttk.Frame(notebook)
    notebook.add(book_frame, text='Book Appointment')

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

    refresh_prescriptions()

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

tk.Label(frame_register, text="Full Name:").grid(row=2, column=0)
entry_name = tk.Entry(frame_register)
entry_name.grid(row=2, column=1)

tk.Label(frame_register, text="Role:").grid(row=3, column=0)
role_var = tk.StringVar(value="Patient")
tk.Radiobutton(frame_register, text="Patient", variable=role_var, value="Patient").grid(row=3, column=1)
tk.Radiobutton(frame_register, text="Doctor", variable=role_var, value="Doctor").grid(row=3, column=2)
tk.Radiobutton(frame_register, text="Admin", variable=role_var, value="Admin").grid(row=3, column=3)

tk.Button(frame_register, text="Register", command=register_user).grid(row=4, column=1)

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

root.mainloop()