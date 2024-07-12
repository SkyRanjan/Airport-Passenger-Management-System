import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_FILE = 'airport_management.db'

def connect_db():
    return sqlite3.connect(DB_FILE)

def execute_query(query, params=None):
    with connect_db() as conn:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        return cur.fetchall()

def create_tables():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS Terminal_Service (
            Service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Service_name TEXT,
            Service_charges REAL,
            Available_time TEXT,
            Status TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Admin (
            Employee_number TEXT PRIMARY KEY,
            Name TEXT,
            Date_of_birth TEXT,
            Phone_number TEXT,
            Service_id INTEGER,
            FOREIGN KEY (Service_id) REFERENCES Terminal_Service(Service_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Passenger (
            Aadhar_number TEXT PRIMARY KEY,
            Name TEXT,
            Phone_number TEXT,
            Age INTEGER,
            Gate_number TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Luggage (
            Luggage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Aadhar_number TEXT,
            Number_of_bags INTEGER,
            Total_weight REAL,
            Status TEXT,
            FOREIGN KEY (Aadhar_number) REFERENCES Passenger(Aadhar_number)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Flight (
            Flight_number TEXT PRIMARY KEY,
            Airline_name TEXT,
            Aeroplane_model TEXT,
            Total_passengers INTEGER,
            Total_weight REAL,
            Gate_number TEXT,
            ETA TEXT,
            ETD TEXT,
            Date TEXT,
            Status TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Passenger_Flight (
            Aadhar_number TEXT,
            Flight_number TEXT,
            PRIMARY KEY (Aadhar_number, Flight_number),
            FOREIGN KEY (Aadhar_number) REFERENCES Passenger(Aadhar_number),
            FOREIGN KEY (Flight_number) REFERENCES Flight(Flight_number)
        )
        """
        
    ]
    
    for query in queries:
        execute_query(query)

class AirportManagementSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Airport Management System")
        self.master.geometry("800x600")
        
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()
        
        tk.Label(self.master, text="Airport Management System", font=("Arial", 24)).pack(pady=20)
        
        ttk.Button(self.master, text="Passenger", command=self.passenger_menu).pack(pady=10)
        ttk.Button(self.master, text="Admin", command=self.admin_login).pack(pady=10)
        ttk.Button(self.master, text="Exit", command=self.master.quit).pack(pady=10)

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def passenger_menu(self):
        self.clear_window()
        
        tk.Label(self.master, text="Passenger Menu", font=("Arial", 20)).pack(pady=20)
        
        ttk.Button(self.master, text="New Passenger", command=self.new_passenger_form).pack(pady=10)
        ttk.Button(self.master, text="Existing Passenger", command=self.existing_passenger_login).pack(pady=10)
        ttk.Button(self.master, text="Back to Main Menu", command=self.create_main_menu).pack(pady=10)

    def new_passenger_form(self):
        self.clear_window()
        
        tk.Label(self.master, text="New Passenger Registration", font=("Arial", 20)).pack(pady=20)
        
        fields = ['Name', 'Age', 'Phone Number', 'Flight Number', 'Aadhar Number', 'Gate Number']
        entries = {}
        
        for field in fields:
            frame = tk.Frame(self.master)
            frame.pack(pady=5)
            tk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT)
            entries[field] = entry
        
        ttk.Button(self.master, text="Submit", command=lambda: self.add_new_passenger(entries)).pack(pady=10)
        ttk.Button(self.master, text="Back", command=self.passenger_menu).pack(pady=10)

    def add_new_passenger(self, entries):
        # Extract values from entries
        name = entries['Name'].get()
        age = entries['Age'].get()
        phone = entries['Phone Number'].get()
        flight_number = entries['Flight Number'].get()
        aadhar = entries['Aadhar Number'].get()
        gate = entries['Gate Number'].get()
        
        # Perform validation here
        if not all([name, age, phone, flight_number, aadhar, gate]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        query = """
        INSERT INTO Passenger (Aadhar_number, Name, Phone_number, Age, Gate_number)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (aadhar, name, phone, age, gate))

        query = """
        INSERT INTO Passenger_Flight (Aadhar_number, Flight_number)
        VALUES (?, ?)
        """
        execute_query(query, (aadhar, flight_number))

        messagebox.showinfo("Success", "Passenger added successfully.")

        # Ask if user wants to add luggage
        if messagebox.askyesno("Add Luggage", "Do you want to add luggage for this passenger?"):
            self.add_luggage_form(aadhar)
        else:
            self.passenger_menu()

    def add_luggage_form(self, aadhar):
        self.clear_window()
        
        tk.Label(self.master, text="Add Luggage", font=("Arial", 20)).pack(pady=20)
        
        fields = ['Number of Bags', 'Total Weight']
        entries = {}
        
        for field in fields:
            frame = tk.Frame(self.master)
            frame.pack(pady=5)
            tk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT)
            entries[field] = entry
        
        ttk.Button(self.master, text="Submit", command=lambda: self.add_new_luggage(aadhar, entries)).pack(pady=10)
        ttk.Button(self.master, text="Skip", command=self.passenger_menu).pack(pady=10)

    def add_new_luggage(self, aadhar, entries):
        # Extract values from entries
        num_bags = entries['Number of Bags'].get()
        total_weight = entries['Total Weight'].get()
        
        # Perform validation here
        if not all([num_bags, total_weight]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        query = """
        INSERT INTO Luggage (Aadhar_number, Number_of_bags, Total_weight, Status)
        VALUES (?, ?, ?, ?)
        """
        execute_query(query, (aadhar, num_bags, total_weight, "Pending"))

        messagebox.showinfo("Success", "Luggage added successfully.")
        self.passenger_menu()

    def existing_passenger_login(self):
        self.clear_window()
        
        tk.Label(self.master, text="Existing Passenger Login", font=("Arial", 20)).pack(pady=20)
        
        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text="Aadhar Number:").pack(side=tk.LEFT)
        aadhar_entry = tk.Entry(frame)
        aadhar_entry.pack(side=tk.LEFT)
        
        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text="Phone Number:").pack(side=tk.LEFT)
        phone_entry = tk.Entry(frame)
        phone_entry.pack(side=tk.LEFT)
        
        ttk.Button(self.master, text="Login", command=lambda: self.authenticate_passenger(aadhar_entry.get(), phone_entry.get())).pack(pady=10)
        ttk.Button(self.master, text="Back", command=self.passenger_menu).pack(pady=10)

    def authenticate_passenger(self, aadhar, phone):
        query = """
        SELECT * FROM Passenger WHERE Aadhar_number = ? AND Phone_number = ?
        """
        result = execute_query(query, (aadhar, phone))

        if result:
            self.passenger_dashboard(aadhar)
        else:
            messagebox.showerror("Error", "Authentication failed.")

    def passenger_dashboard(self, aadhar):
        self.clear_window()
        
        tk.Label(self.master, text="Passenger Dashboard", font=("Arial", 20)).pack(pady=20)
        
        ttk.Button(self.master, text="Track Luggage", command=lambda: self.track_luggage(aadhar)).pack(pady=10)
        ttk.Button(self.master, text="Terminal Services", command=self.show_terminal_services).pack(pady=10)
        ttk.Button(self.master, text="Check Flight Status", command=lambda: self.check_flight_status(aadhar)).pack(pady=10)
        ttk.Button(self.master, text="Back to Passenger Menu", command=self.passenger_menu).pack(pady=10)

    def track_luggage(self, aadhar):
        query = """
        SELECT * FROM Luggage WHERE Aadhar_number = ?
        """
        result = execute_query(query, (aadhar,))
        
        if result:
            luggage_info = ""
            for luggage in result:
                luggage_info += f"Luggage ID: {luggage[0]}\n"
                luggage_info += f"Number of Bags: {luggage[2]}\n"
                luggage_info += f"Total Weight: {luggage[3]}\n"
                luggage_info += f"Status: {luggage[4]}\n\n"
            messagebox.showinfo("Luggage Information", luggage_info)
        else:
            messagebox.showinfo("Luggage Information", "No luggage found for this passenger.")

    def check_flight_status(self, aadhar):
        query = """
        SELECT f.Flight_number, fs.Status
        FROM Passenger_Flight pf
        JOIN Flight f ON pf.Flight_number = f.Flight_number
        JOIN flight_status fs ON f.Flight_number = fs.Status
        WHERE fs.Flight_number = ?
        """
        result = execute_query(query, (aadhar,))
        
        if result:
            flight_info = ""
            for flight in result:
                flight_info += f"Flight Number: {flight[0]}\n"
                flight_info += f"Status: {flight[1]}\n\n"
            messagebox.showinfo("Flight Information", flight_info)
        else:
            messagebox.showinfo("Flight Information", "No flight information found for this passenger.")

    def admin_login(self):
        self.clear_window()
        
        tk.Label(self.master, text="Admin Login", font=("Arial", 20)).pack(pady=20)
        
        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text="Employee Number:").pack(side=tk.LEFT)
        emp_num_entry = tk.Entry(frame)
        emp_num_entry.pack(side=tk.LEFT)
        
        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text="Date of Birth (YYYY-MM-DD):").pack(side=tk.LEFT)
        dob_entry = tk.Entry(frame)
        dob_entry.pack(side=tk.LEFT)
        
        ttk.Button(self.master, text="Login", command=lambda: self.authenticate_admin(emp_num_entry.get(), dob_entry.get())).pack(pady=10)
        ttk.Button(self.master, text="Back to Main Menu", command=self.create_main_menu).pack(pady=10)

    def authenticate_admin(self, emp_num, dob):
        query = """
        SELECT * FROM Admin WHERE Employee_number = ? AND Date_of_birth = ?
        """
        result = execute_query(query, (emp_num, dob))

        if result:
            self.admin_dashboard()
        else:
            messagebox.showerror("Error", "Authentication failed.")

    def admin_dashboard(self):
        self.clear_window()
        
        tk.Label(self.master, text="Admin Dashboard", font=("Arial", 20)).pack(pady=20)
        
        ttk.Button(self.master, text="Track Passenger", command=self.track_passenger_form).pack(pady=10)
        ttk.Button(self.master, text="Track Flight", command=self.track_flight_form).pack(pady=10)
        ttk.Button(self.master, text="Track Luggage", command=self.track_luggage_by_id_form).pack(pady=10)
        ttk.Button(self.master, text="Add Flight", command=self.add_flight_form).pack(pady=10)
        ttk.Button(self.master, text="Change Status", command=self.change_status_menu).pack(pady=10)
        ttk.Button(self.master, text="List Terminal Services", command=self.show_terminal_services).pack(pady=10)
        ttk.Button(self.master, text="Back to Main Menu", command=self.create_main_menu).pack(pady=10)
    
    def change_status_menu(self):
        self.clear_window()
        
        tk.Label(self.master, text="Change Status", font=("Arial", 20)).pack(pady=20)
        
        ttk.Button(self.master, text="Passenger Status", command=lambda: self.change_status_form("passenger")).pack(pady=10)
        ttk.Button(self.master, text="Flight Status", command=lambda: self.change_status_form("flight")).pack(pady=10)
        ttk.Button(self.master, text="Luggage Status", command=lambda: self.change_status_form("luggage")).pack(pady=10)
        ttk.Button(self.master, text="Back to Admin Dashboard", command=self.admin_dashboard).pack(pady=10)

    def change_status_form(self, status_type):
        self.clear_window()
        
        tk.Label(self.master, text=f"Change {status_type.capitalize()} Status", font=("Arial", 20)).pack(pady=20)
        
        if status_type == "passenger":
            id_label = "Aadhar Number"
            id_column = "Aadhar_number"
            table = "passenger_status"
            status_table = "set_passenger_status"
        elif status_type == "flight":
            id_label = "Flight Number"
            id_column = "Flight_number"
            table = "Flight_status"
            status_table = "set_flight_status"
        else:  # luggage
            id_label = "Luggage ID"
            id_column = "Luggage_id"
            table = "Luggage_status"
            status_table = "set_luggage_status"

        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text=f"{id_label}:").pack(side=tk.LEFT)
        id_entry = tk.Entry(frame)
        id_entry.pack(side=tk.LEFT)

        status_options = self.get_status_options(status_table)
        status_var = tk.StringVar(self.master)
        status_var.set(status_options[0])  # Set default value

        tk.Label(self.master, text="New Status:").pack()
        status_menu = ttk.Combobox(self.master, textvariable=status_var, values=status_options)
        status_menu.pack(pady=10)

        ttk.Button(self.master, text="Update Status", 
                   command=lambda: self.update_status(status_type, id_entry.get(), status_var.get(), id_column, table)).pack(pady=10)
        ttk.Button(self.master, text="Back", command=self.change_status_menu).pack(pady=10)

    def get_status_options(self, status_table):
        try:
            query = f"SELECT status_name FROM {status_table}"
            result = execute_query(query)
            return [status[0] for status in result] if result else []
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            messagebox.showerror("Error", f"Failed to get status options: {e}")
            return []

    def update_status(self, status_type, id_value, new_status, id_column, table):
        if not id_value or not new_status:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        query = f"UPDATE {table} SET Status = ? WHERE {id_column} = ?"
        execute_query(query, (new_status, id_value))

        if status_type == "passenger":
            # Update or insert into passenger_status table
            check_query = "SELECT * FROM passenger_status WHERE Aadhar_number = ?"
            result = execute_query(check_query, (id_value,))
            if result:
                update_query = "UPDATE passenger_status SET Status = ? WHERE Aadhar_number = ?"
            else:
                update_query = "INSERT INTO passenger_status (Status, Aadhar_number) VALUES (?, ?)"
            execute_query(update_query, (new_status, id_value))

        messagebox.showinfo("Success", f"{status_type.capitalize()} status updated successfully.")
        self.change_status_menu()

    def track_passenger_form(self):
        self.clear_window()
        
        tk.Label(self.master, text="Track Passenger", font=("Arial", 20)).pack(pady=20)
        
        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text="Aadhar Number:").pack(side=tk.LEFT)
        aadhar_entry = tk.Entry(frame)
        aadhar_entry.pack(side=tk.LEFT)
        
        ttk.Button(self.master, text="Track", command=lambda: self.track_passenger(aadhar_entry.get())).pack(pady=10)
        ttk.Button(self.master, text="Back", command=self.admin_dashboard).pack(pady=10)

    def track_passenger(self, aadhar):
        query = """
        SELECT p.*, l.Luggage_id, l.Number_of_bags, l.Total_weight, l.Status, f.Flight_number, fs.Status
        FROM Passenger p
        LEFT JOIN Luggage l ON p.Aadhar_number = l.Aadhar_number
        LEFT JOIN Passenger_Flight pf ON p.Aadhar_number = pf.Aadhar_number
        LEFT JOIN Flight f ON pf.Flight_number = f.Flight_number
        LEFT JOIN passenger_status fs ON pf.Aadhar_number=fs.Aadhar_number
        WHERE p.Aadhar_number = ?
        """
        result = execute_query(query, (aadhar,))
        query1 = """SELECT Status FROM passenger_status WHERE Aadhar_number= ?"""
        result1=execute_query(query1, (aadhar,))
        if result:
            passenger_info = f"""
            Name: {result[0][1]}
            Age: {result[0][3]}
            Phone: {result[0][2]}
            Gate Number: {result[0][4]}
            Luggage ID: {result[0][5]}
            Number of Bags: {result[0][6]}
            Total Weight: {result[0][7]}
            Flight Number: {result[0][9]}
            passenger Status: {result1}
            """
            messagebox.showinfo("Passenger Information", passenger_info)
        else:
            messagebox.showinfo("Passenger Information", "Passenger not found.")

    def track_flight_form(self):
        self.clear_window()
        
        tk.Label(self.master, text="Track Flight", font=("Arial", 20)).pack(pady=20)
        
        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text="Flight Number:").pack(side=tk.LEFT)
        flight_entry = tk.Entry(frame)
        flight_entry.pack(side=tk.LEFT)
        
        ttk.Button(self.master, text="Track", command=lambda: self.track_flight(flight_entry.get())).pack(pady=10)
        ttk.Button(self.master, text="Back", command=self.admin_dashboard).pack(pady=10)

    def track_flight(self, flight_num):
        query = "SELECT * FROM Flight WHERE Flight_number = ?"
        query1 = "SELECT Status FROM flight_status WHERE Flight_number = ?"
        result = execute_query(query, (flight_num,))
        stats = execute_query(query1, (flight_num,))
        if stats:
            stats=stats
        else:
            stats = result[0][9]
        if result:
            flight_info = f"""
            Airline: {result[0][1]}
            Model: {result[0][2]}
            Total Passengers: {result[0][3]}
            Total Weight: {result[0][4]}
            Gate: {result[0][5]}
            ETA: {result[0][6]}
            ETD: {result[0][7]}
            Date: {result[0][8]}
            Status: {stats}
            """
            messagebox.showinfo("Flight Information", flight_info)
        else:
            messagebox.showinfo("Flight Information", "Flight not found.")

    def track_luggage_by_id_form(self):
        self.clear_window()

        tk.Label(self.master, text="Track Luggage by ID", font=("Arial", 20)).pack(pady=20)

        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Label(frame, text="Enter Luggage ID:").pack(side=tk.LEFT)
        luggage_id_entry = tk.Entry(frame)
        luggage_id_entry.pack(side=tk.LEFT)

        ttk.Button(self.master, text="Track", command=lambda: self.track_luggage_by_id(luggage_id_entry.get())).pack(pady=10)
        ttk.Button(self.master, text="Back to Dashboard", command=self.admin_dashboard).pack(pady=10)

    def track_luggage_by_id(self, luggage_id):
        query = """
        SELECT * FROM Luggage WHERE Luggage_id = ?
        """
        result = execute_query(query, (luggage_id,))

        if result:
            self.clear_window()
            tk.Label(self.master, text="Luggage Details", font=("Arial", 20)).pack(pady=20)

            tk.Label(self.master, text=f"Luggage ID: {result[0][0]}").pack()
            tk.Label(self.master, text=f"Aadhar Number: {result[0][1]}").pack()
            tk.Label(self.master, text=f"Number of Bags: {result[0][2]}").pack()
            tk.Label(self.master, text=f"Total Weight: {result[0][3]}").pack()
            tk.Label(self.master, text=f"Status: {result[0][4]}").pack()
        else:
            messagebox.showerror("Error", "Luggage ID not found.")
        ttk.Button(self.master, text="Back to Dashboard", command=self.admin_dashboard).pack(pady=10)

    def add_flight_form(self):
        self.clear_window()
        
        tk.Label(self.master, text="Add New Flight", font=("Arial", 20)).pack(pady=20)
        
        fields = ['Flight Number', 'Airline Name', 'Aeroplane Model', 'Total Passengers',
                  'Total Weight', 'Gate Number', 'ETA', 'ETD', 'Date (YYYY-MM-DD)', 'Status']
        entries = {}
        
        for field in fields:
            frame = tk.Frame(self.master)
            frame.pack(pady=5)
            tk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT)
            entries[field] = entry
        
        ttk.Button(self.master, text="Submit", command=lambda: self.add_new_flight(entries)).pack(pady=10)
        ttk.Button(self.master, text="Back", command=self.admin_dashboard).pack(pady=10)

    def add_new_flight(self, entries):
        # Extract values from entries
        flight_number = entries['Flight Number'].get()
        airline_name = entries['Airline Name'].get()
        aeroplane_model = entries['Aeroplane Model'].get()
        total_passengers = entries['Total Passengers'].get()
        total_weight = entries['Total Weight'].get()
        gate_number = entries['Gate Number'].get()
        eta = entries['ETA'].get()
        etd = entries['ETD'].get()
        date = entries['Date (YYYY-MM-DD)'].get()
        status = entries['Status'].get()
        
        # Perform validation here
        if not all([flight_number, airline_name, aeroplane_model, total_passengers, total_weight, gate_number, eta, etd, date, status]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        query = """
        INSERT INTO Flight (Flight_number, Airline_name, Aeroplane_model, Total_passengers,
                            Total_weight, Gate_number, ETA, ETD, Date, Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(query, (flight_number, airline_name, aeroplane_model, total_passengers,
                              total_weight, gate_number, eta, etd, date, status))

        messagebox.showinfo("Success", "Flight added successfully.")
        self.admin_dashboard()

    def show_terminal_services(self):
        query = "SELECT * FROM Terminal_Service"
        result = execute_query(query)
        
        if result:
            service_info = ""
            for service in result:
                service_info += f"Service ID: {service[0]}\n"
                service_info += f"Service Name: {service[1]}\n"
                service_info += f"Service Charges: {service[2]}\n"
                service_info += f"Available Time: {service[3]}\n"
                service_info += f"Status: {service[4]}\n\n"
            messagebox.showinfo("Terminal Services", service_info)
        else:
            messagebox.showinfo("Terminal Services", "No terminal services found.")

if __name__ == "__main__":
    create_tables()
    root = tk.Tk()
    app = AirportManagementSystem(root)
    root.mainloop()
