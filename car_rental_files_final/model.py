import sqlite3
import os
import glob
import logging
import sys
from datetime import datetime

# Setup a hidden log file for actual errors (for the developer only)
logging.basicConfig(filename='system_errors.log', level=logging.ERROR, 
                    format='%(asctime)s %(message)s')

class RentalModel:
    def __init__(self):
        self.db_path = self._get_db_path()
        print(f"[SYSTEM] Connected to Database: {self.db_path}")

    def _get_db_path(self):
        """Finds the DB file responsibly in Dev and EXE modes."""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        db_files = glob.glob(os.path.join(base_dir, "*.db"))
        valid_dbs = [f for f in db_files if os.path.getsize(f) > 0]
        
        if not valid_dbs:
            raise FileNotFoundError(f"CRITICAL: No Database found in {base_dir}")
            
        return max(valid_dbs, key=os.path.getsize)

    def connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row #you get the resuts as dictionaries
        return conn

    def _sanitize_error(self, e):
        """Internal method to mask SQL errors."""
        err_str = str(e).lower()
        logging.error(f"SQL Error: {e}") 
        
        if "unique constraint" in err_str:
            return "Operation failed: Duplicate record detected."
        elif "foreign key" in err_str or "constraint failed" in err_str:
            return "Operation failed: Record is linked to active data and cannot be modified."
        elif "no such table" in err_str:
            return "System Error: Data structure not found. Contact IT."
        else:
            return "An unexpected system error occurred."

    def execute_query(self, query, params=(), commit=False, fetch_one=False, fetch_all=False):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetch_one:
                row = cursor.fetchone()
                result = dict(row) if row else None
            elif fetch_all:
                result = [dict(row) for row in cursor.fetchall()]
            
            if commit:
                conn.commit()
                if query.strip().upper().startswith("INSERT"):
                    result = cursor.lastrowid

            return True, result
        except sqlite3.Error as e:
            safe_msg = self._sanitize_error(e)
            return False, safe_msg
        finally:
            if conn: conn.close()

    # ==========================
    #      ADMIN & USER OPS
    # ==========================

    def create_indexes(self):
        queries = [
            "CREATE INDEX IF NOT EXISTS idx_customer_name ON Customer (full_name);",
            "CREATE INDEX IF NOT EXISTS idx_car_plate ON Car (license_plate);",
            "CREATE INDEX IF NOT EXISTS idx_res_customer ON Reservation (customer_id);"
        ]
        for q in queries: self.execute_query(q, commit=True)

    # --- CUSTOMER OPS ---
    def get_all_customers(self):
        return self.execute_query("SELECT customer_id, full_name, email, phone FROM Customer", fetch_all=True)

    def add_customer(self, data):
        query = "INSERT INTO Customer (driver_license, full_name, birth_date, address, phone, email) VALUES (?,?,?,?,?,?)"
        params = (data.get('license'), data['name'], data['dob'], data['address'], data['phone'], data['email'])
        return self.execute_query(query, params, commit=True)

    def update_customer(self, c_id, field, value):
        if field not in ['phone', 'email']: return False, "Invalid field selection."
        query = f"UPDATE Customer SET {field} = ? WHERE customer_id = ?"
        return self.execute_query(query, (value, c_id), commit=True)

    def delete_customer(self, c_id):
        """Safe Delete: Only allows deletion if the customer has NO reservation history."""
        try:
            query = "SELECT COUNT(*) as count FROM Reservation WHERE customer_id = ?"
            success, row = self.execute_query(query, (c_id,), fetch_one=True)
            
            if success and row and row['count'] > 0:
                return False, f"Cannot delete: Customer has {row['count']} records in history. (Legal/Financial Constraint)"

            return self.execute_query("DELETE FROM Customer WHERE customer_id = ?", (c_id,), commit=True)
        except Exception as e:
            return False, str(e)

    def get_customer_by_email(self, email):
        return self.execute_query("SELECT customer_id FROM Customer WHERE email=?", (email,), fetch_one=True)

    # --- CAR OPS ---
    def get_all_cars(self):
        query = "SELECT car_id, brand, model, license_plate, price_per_day, availability, mileage FROM Car"
        return self.execute_query(query, fetch_all=True)

    def get_available_cars_for_booking(self, cat_id, loc_id):
        query = "SELECT car_id, brand, model, price_per_day, gearbox, fuel, seats, bags FROM Car WHERE category_id = ? AND location_id = ? AND availability = 1"
        return self.execute_query(query, (cat_id, loc_id), fetch_all=True)

    def add_car(self, d):
        query = "INSERT INTO Car (license_plate, brand, model, price_per_day, color, gearbox, mileage, availability, location_id, category_id) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)"
        params = (d['plate'], d['brand'], d['model'], d['price'], d['color'], d['gear'], d['mil'], d['loc_id'], d['cat_id'])
        return self.execute_query(query, params, commit=True)

    def update_car_price(self, c_id, new_price):
        return self.execute_query("UPDATE Car SET price_per_day = ? WHERE car_id = ?", (new_price, c_id), commit=True)
    
    def update_car_mileage(self, c_id, new_mil):
        """Updates the car's current mileage."""
        try:
            return self.execute_query("UPDATE Car SET mileage = ? WHERE car_id = ?", (new_mil, c_id), commit=True)
        except Exception as e:
            return False, str(e)

    def retire_car(self, c_id):
        """Soft Delete with Safety Check."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            query = """
                SELECT reservation_id FROM Reservation 
                WHERE car_id = ? 
                AND drop_off_date >= ? 
                AND status = 'Confirmed'
            """
            success, rows = self.execute_query(query, (c_id, today), fetch_all=True)
            if success and rows:
                return False, f"Cannot retire: Car has {len(rows)} active/future booking(s). Please Cancel them first."

            return self.execute_query("UPDATE Car SET availability = 0 WHERE car_id = ?", (c_id,), commit=True)
        except Exception as e:
            return False, f"Database Error: {str(e)}"

    def activate_car(self, c_id):
        """Re-activates a retired car."""
        return self.execute_query("UPDATE Car SET availability = 1 WHERE car_id = ?", (c_id,), commit=True)

    # --- RESERVATION OPS ---
    def get_all_reservations(self):
        query = """
        SELECT r.reservation_id, c.full_name, car.brand, car.model, r.pick_up_date, r.drop_off_date, r.status 
        FROM Reservation r 
        JOIN Customer c ON r.customer_id = c.customer_id 
        JOIN Car car ON r.car_id = car.car_id
        """
        return self.execute_query(query, fetch_all=True)

    def add_reservation(self, d):
        query = "INSERT INTO Reservation (pick_up_date, drop_off_date, car_id, pick_up_location, drop_off_location, customer_id, insurance_preference, category_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        params = (d['p_date'], d['d_date'], d['car_id'], d['p_loc'], d['d_loc'], d['cust_id'], d['ins_id'], d['cat_id'])
        return self.execute_query(query, params, commit=True)

    def cancel_reservation(self, res_id):
        """Soft Cancel."""
        try:
            success, row = self.execute_query("SELECT reservation_id FROM Reservation WHERE reservation_id = ?", (res_id,), fetch_one=True)
            if not success or not row: return False, "Reservation ID not found."
            return self.execute_query("UPDATE Reservation SET status = 'Cancelled' WHERE reservation_id = ?", (res_id,), commit=True)
        except Exception as e:
            return False, str(e)

    def get_conflicting_reservations(self, start_str, end_str):
        query = "SELECT car_id FROM Reservation WHERE (pick_up_date <= ? AND drop_off_date >= ?) AND status = 'Confirmed'"
        return self.execute_query(query, (end_str, start_str), fetch_all=True)

    # --- EMPLOYEE OPS ---
    def get_all_employees(self):
        return self.execute_query("SELECT employee_id, name, surname, email, phone FROM Employee", fetch_all=True)

    def add_employee(self, d):
        query = "INSERT INTO Employee (name, surname, email, phone, afm) VALUES (?, ?, ?, ?, ?)"
        params = (d['name'], d['surname'], d['email'], d['phone'], d['afm'])
        return self.execute_query(query, params, commit=True)

    def update_employee(self, e_id, field, val):
        if field not in ['phone', 'email']: return False, "Invalid field."
        query = f"UPDATE Employee SET {field} = ? WHERE employee_id = ?"
        return self.execute_query(query, (val, e_id), commit=True)

    def delete_employee(self, e_id):
        """Safe Delete: Checks for Work History before deleting."""
        try:
            # 1. Check PickUp History
            success, row = self.execute_query("SELECT COUNT(*) as c FROM PickUp WHERE employee_id = ?", (e_id,), fetch_one=True)
            if success and row['c'] > 0:
                return False, f"Cannot delete: Employee has logged {row['c']} Pick-Ups."

            # 2. Check DropOff History
            success, row = self.execute_query("SELECT COUNT(*) as c FROM DropOff WHERE employee_id = ?", (e_id,), fetch_one=True)
            if success and row['c'] > 0:
                return False, f"Cannot delete: Employee has logged {row['c']} Drop-Offs."

            # 3. Safe to delete
            return self.execute_query("DELETE FROM Employee WHERE employee_id = ?", (e_id,), commit=True)
        except Exception as e:
            return False, str(e)

    # --- UTILS (Pickups, Payments, Meta) ---
    def get_locations(self): 
        return self.execute_query("SELECT location_id as id, address FROM Location", fetch_all=True)
    def get_categories(self): 
        return self.execute_query("SELECT category_id as id, category_name FROM Category", fetch_all=True)
    
    def add_payment(self, res_id, amount, cust_id):
        return self.execute_query("INSERT INTO Payment (reservation_id, total_amount, customer_id, security_deposit, car_price) VALUES (?,?,?, 50, 0)", (res_id, amount, cust_id), commit=True)
    
    def get_all_payments(self):
        return self.execute_query("SELECT p.payment_number, p.total_amount, c.full_name, p.reservation_id FROM Payment p JOIN Customer c ON p.customer_id = c.customer_id", fetch_all=True)

    def add_pickup_dropoff(self, table, d):
        state_col = "pick_up_state" if table == "PickUp" else "drop_off_state"
        date_col = "true_pick_up_date" if table == "PickUp" else "true_drop_off_date"
        query = f"INSERT INTO {table} (employee_id, reservation_id, location_id, {state_col}, {date_col}) VALUES (?,?,?,?,?)"
        return self.execute_query(query, (d['emp_id'], d['res_id'], d['loc_id'], d['state'], d['date']), commit=True)

    def get_pickups_dropoffs(self, table):
        col_prefix = "pick_up" if table == "PickUp" else "drop_off"
        query = f"SELECT x.{col_prefix}_id as id, x.reservation_id, e.surname, x.{col_prefix}_state as state, x.true_{col_prefix}_date as date FROM {table} x JOIN Employee e ON x.employee_id = e.employee_id"
        return self.execute_query(query, fetch_all=True)
    
    # --- STATISTICS & REPORTS ---
    def get_stats(self):
        stats = {}
        s, r = self.execute_query("SELECT SUM(total_amount) FROM Payment", fetch_one=True)
        stats['revenue'] = list(r.values())[0] if s and r else 0
        s, r = self.execute_query("SELECT COUNT(*) FROM Car WHERE availability = 1", fetch_one=True)
        stats['avail'] = list(r.values())[0] if s and r else 0
        s, r = self.execute_query("SELECT COUNT(*) FROM Car WHERE availability = 0", fetch_one=True)
        stats['rented'] = list(r.values())[0] if s and r else 0
        return stats

    def get_top_customers(self):
        query = """
        SELECT c.full_name, SUM(p.total_amount) as spent 
        FROM Customer c 
        JOIN Payment p ON c.customer_id = p.customer_id 
        GROUP BY c.customer_id 
        ORDER BY spent DESC 
        LIMIT 3
        """
        return self.execute_query(query, fetch_all=True)

    def get_avg_duration(self):
        query = "SELECT AVG(julianday(drop_off_date) - julianday(pick_up_date)) FROM Reservation"
        success, row = self.execute_query(query, fetch_one=True)
        if success and row:
            val = list(row.values())[0]
            return round(val, 1) if val else 0
        return 0
    
    # --- ADMIN FEATURES ---
    def get_active_future_reservations(self):
        today = datetime.now().strftime("%Y-%m-%d")
        query = """
        SELECT r.reservation_id, c.full_name, car.brand, car.model, r.pick_up_date, r.drop_off_date, r.status
        FROM Reservation r 
        JOIN Customer c ON r.customer_id = c.customer_id 
        JOIN Car car ON r.car_id = car.car_id
        WHERE r.drop_off_date >= ? AND r.status = 'Confirmed'
        ORDER BY r.pick_up_date ASC
        """
        return self.execute_query(query, (today,), fetch_all=True)

    def get_most_popular_store(self):
        query = """
        SELECT l.address, COUNT(r.reservation_id) as usage_count
        FROM Reservation r
        JOIN Location l ON r.pick_up_location = l.location_id
        GROUP BY l.location_id
        ORDER BY usage_count DESC
        LIMIT 1
        """
        return self.execute_query(query, fetch_one=True)

    def get_employee_work_history(self, emp_id):
        query = """
        SELECT r.reservation_id, r.pick_up_date as action_date, 'PickUp' as type
        FROM PickUp p
        JOIN Reservation r ON p.reservation_id = r.reservation_id
        WHERE p.employee_id = ?
        
        UNION ALL
        
        SELECT r.reservation_id, r.drop_off_date as action_date, 'DropOff' as type
        FROM DropOff d
        JOIN Reservation r ON d.reservation_id = r.reservation_id
        WHERE d.employee_id = ?
        ORDER BY action_date DESC
        """
        return self.execute_query(query, (emp_id, emp_id), fetch_all=True)