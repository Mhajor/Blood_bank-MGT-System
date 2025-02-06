import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

# Database Connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="blood_bank"
    )

# Admin Login Function
def login():
    username = entry_username.get()
    password = entry_password.get()
    
    if username == "admin" and password == "p@ssw0rd":  # Default admin credentials
        root.destroy()  # Close login window
        open_homepage()  # Open the homepage
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

# Homepage - Displays Blood Inventory
def open_homepage():
    homepage = tk.Tk()
    homepage.title("FINNEY HOSPITAL BLOOD BANK MGT SYSTEM")
    homepage.geometry("500x500")  # Increase size for visibility

    tk.Label(homepage, text="FINNEY HOSPITAL BLOOD INVENTORY", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    frame = tk.Frame(homepage)
    frame.grid(row=1, column=0, columnspan=2)

    tk.Label(frame, text="Blood Group", font=("Arial", 12, "bold"), width=15).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(frame, text="Units Available", font=("Arial", 12, "bold"), width=15).grid(row=0, column=1, padx=10, pady=5)

    # Fetch Blood Inventory
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM blood_inventory")
    rows = cursor.fetchall()

    if not rows:  # If the table is empty, show a message
        tk.Label(homepage, text="No blood inventory found. Please add records.", font=("Arial", 12, "bold"), fg="red").grid(row=2, column=0, columnspan=2, pady=10)

    # Display Inventory
    for i, row in enumerate(rows, start=1):
        tk.Label(frame, text=row[0], font=("Arial", 12), width=15).grid(row=i, column=0, padx=10, pady=5)
        tk.Label(frame, text=row[1], font=("Arial", 12), width=15).grid(row=i, column=1, padx=10, pady=5)

    # Buttons should always be visible
    button_frame = tk.Frame(homepage)
    button_frame.grid(row=3, column=0, columnspan=2, pady=20)

    tk.Button(button_frame, text="Request Blood", command=request_blood, font=("Arial", 12), bg="red", fg="white").grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Donate Blood", command=donate_blood, font=("Arial", 12), bg="green", fg="white").grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Refresh", command=lambda: [homepage.destroy(), open_homepage()], font=("Arial", 12), bg="blue", fg="white").grid(row=1, column=0, columnspan=2, pady=10)

    homepage.mainloop()

# Blood Request Function
def request_blood():
    req_window = tk.Toplevel()
    req_window.title("Request Blood")

    tk.Label(req_window, text="Enter Blood Group:").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(req_window, text="Units Required:").grid(row=1, column=0, padx=10, pady=5)

    entry_group = tk.Entry(req_window)
    entry_units = tk.Entry(req_window)
    entry_group.grid(row=0, column=1, padx=10, pady=5)
    entry_units.grid(row=1, column=1, padx=10, pady=5)

    def process_request():
        blood_group = entry_group.get().upper()
        units_needed = int(entry_units.get())

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT units_available FROM blood_inventory WHERE blood_group=%s", (blood_group,))
        result = cursor.fetchone()

        if result and result[0] >= units_needed:
            cursor.execute("UPDATE blood_inventory SET units_available = units_available - %s WHERE blood_group=%s",
                           (units_needed, blood_group))
            db.commit()
            messagebox.showinfo("Success", "Blood request successful!")
        else:
            messagebox.showerror("Error", "Not enough blood available! or invalid blood_group entered")

        db.close()
        req_window.destroy()

    tk.Button(req_window, text="Submit", command=process_request, bg="blue", fg="white").grid(row=2, column=1, pady=10)

# Blood Donation Function
def donate_blood():
    don_window = tk.Toplevel()
    don_window.title("Donate Blood")

    tk.Label(don_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(don_window, text="Blood Group:").grid(row=1, column=0, padx=10, pady=5)
    tk.Label(don_window, text="Contact:").grid(row=2, column=0, padx=10, pady=5)
    tk.Label(don_window, text="Units to Donate:").grid(row=3, column=0, padx=10, pady=5)

    entry_name = tk.Entry(don_window)
    entry_group = tk.Entry(don_window)
    entry_contact = tk.Entry(don_window)
    entry_units = tk.Entry(don_window)

    entry_name.grid(row=0, column=1, padx=10, pady=5)
    entry_group.grid(row=1, column=1, padx=10, pady=5)
    entry_contact.grid(row=2, column=1, padx=10, pady=5)
    entry_units.grid(row=3, column=1, padx=10, pady=5)

    def process_donation():
        name = entry_name.get()
        blood_group = entry_group.get().upper()
        contact = entry_contact.get()
        units_donated = int(entry_units.get())
        donation_date = datetime.today().strftime('%Y-%m-%d')

        db = connect_db()
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO donors (name, blood_group, contact, donation_date) VALUES (%s, %s, %s, %s)",
                           (name, blood_group, contact, donation_date))
            cursor.execute("INSERT INTO blood_inventory (blood_group, units_available) VALUES (%s, %s) ON DUPLICATE KEY UPDATE units_available = units_available + %s",
                           (blood_group, units_donated, units_donated))
            db.commit()
            messagebox.showinfo("Success", f"Donation recorded successfully! {units_donated} units added.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            db.close()
            don_window.destroy()

    tk.Button(don_window, text="Submit", command=process_donation, bg="green", fg="white").grid(row=4, column=1, pady=10)

# Login Screen
root = tk.Tk()
root.title("Admin Login")
root.geometry("300x200")

tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5)

entry_username = tk.Entry(root)
entry_password = tk.Entry(root, show="*")

entry_username.grid(row=0, column=1, padx=10, pady=5)
entry_password.grid(row=1, column=1, padx=10, pady=5)

tk.Button(root, text="Login", command=login, bg="blue", fg="white").grid(row=2, column=1, pady=10)

root.mainloop()
