import os
import random
import re
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

# -----------------------------
# Data Structure: Booking Class
# -----------------------------
class Booking:
    def __init__(self, booking_id, name, contact, game, start_time, end_time, fee, date=None):
        self.booking_id = booking_id
        self.name = name
        self.contact = contact
        self.game = game
        self.start_time = start_time
        self.end_time = end_time
        self.fee = fee
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")

    def __str__(self):
        return (f"ID: {self.booking_id} | Name: {self.name} | Contact: {self.contact} "
                f"| Game: {self.game} | Time: {self.start_time}-{self.end_time} "
                f"| Fee: {self.fee} | Date: {self.date}")


# -----------------------------
# File Handling Functions
# -----------------------------
def save_to_file(bookings):
    with open("bookings.txt", "w") as f:
        for b in bookings:
            f.write(f"{b.booking_id},{b.name},{b.contact},{b.game},{b.start_time},{b.end_time},{b.fee},{b.date}\n")


def load_from_file():
    bookings = []
    if os.path.exists("bookings.txt"):
        with open("bookings.txt", "r") as f:
            for line in f:
                data = line.strip().split(",")
                if len(data) == 8:
                    bookings.append(Booking(*data))
    return bookings


# -----------------------------
# Algorithms
# -----------------------------
def is_conflict(bookings, game, start, end):
    for b in bookings:
        try:
            if b.game.lower() == game.lower():
                if not (int(end) <= int(b.start_time) or int(start) >= int(b.end_time)):
                    return True
        except Exception:
            continue
    return False


def sort_bookings(bookings):
    n = len(bookings)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if bookings[j].name.lower() > bookings[j + 1].name.lower():
                bookings[j], bookings[j + 1] = bookings[j + 1], bookings[j]
    save_to_file(bookings)
    messagebox.showinfo("Sorted", "Bookings sorted by name!")


# -----------------------------
# GUI Logic
# -----------------------------
class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏟️ Olympic Sports City Booking System")
        self.root.geometry("700x500")
        self.root.configure(bg="#e3f2fd")

        # Load bookings once at start
        self.bookings = load_from_file()

        title = tk.Label(root, text="Olympic Sports City Booking System", font=("Arial", 20, "bold"), bg="#90caf9")
        title.pack(fill="x", pady=10)

        # Buttons
        btns = [
            ("Add Booking", self.add_booking),
            ("View Bookings", self.view_bookings),
            ("Search Booking", self.search_booking),
            ("Cancel Booking", self.cancel_booking),
            ("Sort Bookings", lambda: sort_bookings(self.bookings)),
            ("Fee Structure", self.fee_structure),
            ("Exit", root.quit)
        ]

        for text, cmd in btns:
            tk.Button(root, text=text, command=cmd, font=("Arial", 12), bg="#64b5f6", fg="white",
                      width=25, pady=5, relief="raised").pack(pady=5)

    # Add Booking
    def add_booking(self):
        win = tk.Toplevel(self.root)
        win.title("Add Booking")
        win.geometry("420x480")
        win.configure(bg="#bbdefb")

        labels = ["Name", "Contact", "Game", "Start Time (HH)", "End Time (HH)"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(win, text=label, bg="#bbdefb").pack(pady=6)
            entry = tk.Entry(win)
            entry.pack(ipadx=2, ipady=2)
            entries[label] = entry

        def submit():
            # Reload latest bookings from disk to avoid conflicts with other instances/actions
            self.bookings = load_from_file()

            name = entries["Name"].get().strip()
            contact = entries["Contact"].get().strip()
            game = entries["Game"].get().strip()
            start = entries["Start Time (HH)"].get().strip()
            end = entries["End Time (HH)"].get().strip()

            # Name validation: allow letters and spaces (e.g., "Muhammad Ali")
            if not name or not re.match(r"^[A-Za-z ]+$", name):
                messagebox.showerror("Error", "Name must contain only letters and spaces (no digits/symbols).")
                return

            # Contact validation: digits only, length 7-15 (covers local/international-ish)
            if not contact.isdigit() or not (7 <= len(contact) <= 15):
                messagebox.showerror("Error", "Contact must be numeric and 7–15 digits long.")
                return

            if not game:
                messagebox.showerror("Error", "Please enter game name.")
                return

            # Time validation
            try:
                start_i = int(start)
                end_i = int(end)
            except ValueError:
                messagebox.showerror("Error", "Start and End must be numeric hours (HH).")
                return

            if not (0 <= start_i < 24 and 0 < end_i <= 24 and start_i < end_i):
                messagebox.showerror("Error", "Enter valid hours (0–24) and ensure start < end.")
                return

            # Conflict check
            if is_conflict(self.bookings, game, start_i, end_i):
                messagebox.showerror("Error", "Time slot already booked for this game.")
                return

            # Fee calculation
            fee_per_hour = {
                "football": 500,
                "cricket": 700,
                "tennis": 400,
                "badminton": 300,
                "basketball": 450,
                "snooker": 350,
                "volleyball": 400
            }
            fee = fee_per_hour.get(game.lower(), 500) * (end_i - start_i)

            # Generate unique ID (safe)
            while True:
                booking_id = str(random.randint(1000, 9999))
                if not any(b.booking_id == booking_id for b in self.bookings):
                    break

            new_booking = Booking(booking_id, name, contact, game, str(start_i), str(end_i), str(fee))
            self.bookings.append(new_booking)
            save_to_file(self.bookings)
            messagebox.showinfo("Success", f"Booking added successfully!\nID: {booking_id}\nFee: {fee}")
            win.destroy()

        tk.Button(win, text="Submit", command=submit, bg="#64b5f6", fg="white").pack(pady=18)

    # View Bookings
    def view_bookings(self):
        # Reload to show latest
        self.bookings = load_from_file()
        win = tk.Toplevel(self.root)
        win.title("All Bookings")
        win.geometry("700x420")
        win.configure(bg="#e3f2fd")

        box = tk.Text(win, width=85, height=22, wrap="word")
        box.pack(pady=10, padx=6)

        if not self.bookings:
            box.insert("end", "No bookings found.")
        else:
            for b in self.bookings:
                box.insert("end", str(b) + "\n")

    # Search Booking
    def search_booking(self):
        # Reload data
        self.bookings = load_from_file()
        key = simpledialog.askstring("Search", "Enter Booking ID or Name or Game:")
        if not key:
            return

        key_lower = key.lower()
        found = [b for b in self.bookings if key_lower in b.booking_id.lower() or key_lower in b.name.lower() or key_lower in b.game.lower()]

        if not found:
            messagebox.showinfo("Search", "No matching booking found.")
        else:
            result = "\n".join(str(b) for b in found)
            messagebox.showinfo("Results", result)

    # Cancel Booking
    def cancel_booking(self):
        # Reload data
        self.bookings = load_from_file()
        key = simpledialog.askstring("Cancel", "Enter Booking ID to cancel:")
        if not key:
            return

        for b in self.bookings:
            if b.booking_id == key:
                if messagebox.askyesno("Confirm", f"Cancel booking {key} for {b.name}?"):
                    self.bookings.remove(b)
                    save_to_file(self.bookings)
                    messagebox.showinfo("Cancelled", "Booking cancelled successfully!")
                return
        messagebox.showerror("Error", "Booking not found!")

    # Fee Structure
    def fee_structure(self):
        structure = (
            "Football   : 500/hour\n"
            "Cricket    : 700/hour\n"
            "Tennis     : 400/hour\n"
            "Badminton  : 300/hour\n"
            "Basketball : 450/hour\n"
            "Snooker    : 350/hour\n"
            "Volleyball : 400/hour"
        )
        messagebox.showinfo("Fee Structure", structure)


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()
