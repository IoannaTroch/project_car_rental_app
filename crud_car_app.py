import sqlite3


def get_connection():
    return sqlite3.connect('car_rental_db_attemp4.db', timeout=20)

def create_indexes():
    """Δημιουργία ευρετηρίων για βελτίωση της ταχύτητας αναζήτησης και των JOIN."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Ευρετήρια για ταχύτερη αναζήτηση βάσει ονόματος και πινακίδας
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_name ON Customer (full_name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_plate ON Car (license_plate);")
            # Ευρετήρια στα Foreign Keys για ταχύτερα JOIN στις κρατήσεις
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_res_customer ON Reservation (customer_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_res_car ON Reservation (car_id);")
            # Ευρετήριο στις ημερομηνίες κρατήσεων
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_res_dates ON Reservation (pick_up_date, drop_off_date);")
        print(">> Τα indexes δημιουργήθηκαν/ελέγχθηκαν επιτυχώς!")
    except Exception as e:
        print(f">> Σφάλμα στα indexes: {e}")
    finally:
        conn.close()

def create_customer():
    print("\n--- Προσθήκη Νέου Πελάτη ---")
    name = input("Ονοματεπώνυμο: ")
    email = input("Email: ")
    phone = input("Τηλέφωνο: ")
    license = input("Αριθμός Διπλώματος: ")
    address = input("Διεύθυνση: ")
    birth = input("Ημερομηνία Γέννησης (YYYY-MM-DD): ")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()

            query = """INSERT INTO Customer (full_name, email, phone, driver_license, address, birth_date)
                       VALUES (?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (name, email, phone, license, address, birth))
        print(">> Ο πελάτης προστέθηκε επιτυχώς!")
    except Exception as e:
        print(f">> Σφάλμα: {e}")
    finally:
        conn.close()


def read_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, full_name, email, phone FROM Customer")
    rows = cursor.fetchall()
    print("\n--- Λίστα Πελατών ---")
    for row in rows:
        print(f"ID: {row[0]} | Όνομα: {row[1]} | Email: {row[2]} | Τηλ: {row[3]}")
    conn.close()


def update_customer():
    read_customers()
    c_id = input("\nΕισάγετε το ID του πελάτη για ενημέρωση: ")
    print("1. Αλλαγή Τηλεφώνου | 2. Αλλαγή Email")
    choice = input("Επιλογή: ")

    field = "τηλέφωνο" if choice == '1' else "email"
    new_val = input(f"Εισάγετε το νέο {field}: ")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Customer SET {field} = ? WHERE customer_id = ?", (new_val, c_id))
        print(">> Ενημερώθηκε!")
    finally:
        conn.close()


def delete_customer():
    read_customers()
    c_id = input("\nID Πελάτη προς διαγραφή: ")
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM Customer WHERE customer_id = ?", (c_id,))
        print(">> Ο πελάτης διαγράφηκε.")
    except sqlite3.IntegrityError:
        print(">> Σφάλμα: Ο πελάτης έχει ενεργές κρατήσεις[cite: 2, 21].")
    finally:
        conn.close()


def create_car():
    print("\n--- Προσθήκη Αυτοκινήτου ---")
    plate = input("Πινακίδα: ")
    brand = input("Μάρκα: ")
    model = input("Μοντέλο: ")
    price = int(input("Τιμή ανά ημέρα: "))
    color = input("Χρώμα: ")
    gear = input("Κιβώτιο (Manual/Automatic): ")
    mil = int(input("Χιλιόμετρα: "))
    loc_id = int(input("ID Τοποθεσίας: "))
    cat_id = int(input("ID Κατηγορίας: "))

    conn = get_connection()
    try:
        with conn:
            query = """INSERT INTO Car (license_plate, brand, model, price_per_day, color, gearbox,
                                        mileage, availability, location_id, category_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)"""
            conn.execute(query, (plate, brand, model, price, color, gear, mil, loc_id, cat_id))
        print(">> Το αυτοκίνητο προστέθηκε!")
    finally:
        conn.close()


def read_cars():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT car_id, brand, model, license_plate, price_per_day FROM Car")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | {row[1]} {row[2]} | Πινακίδα: {row[3]} | Τιμή: {row[4]}€")
    conn.close()


def update_car_price():
    """Ενημέρωση μόνο της τιμής ανά ημέρα για το αυτοκίνητο."""
    read_cars()
    car_id = input("\nΕισάγετε το ID του αυτοκινήτου για αλλαγή τιμής: ")
    new_price = input("Εισάγετε τη νέα τιμή ανά ημέρα: ")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Ενημέρωση της στήλης price_per_day στον πίνακα Car
            cursor.execute("UPDATE Car SET price_per_day = ? WHERE car_id = ?", (new_price, car_id))
            if cursor.rowcount > 0:
                print(">> Η τιμή του αυτοκινήτου ενημερώθηκε!")
            else:
                print(">> Δεν βρέθηκε αυτοκίνητο με αυτό το ID.")
    finally:
        conn.close()


def delete_car():
    """Διαγραφή αυτοκινήτου με βάση το ID."""
    # Προβολή της λίστας για να διευκολυνθεί ο χρήστης στην επιλογή ID
    read_cars()

    car_id = input("\nΕισάγετε το ID του αυτοκινήτου προς διαγραφή: ")
    conn = get_connection()

    try:
        with conn:
            cursor = conn.cursor()
            # Εκτέλεση της διαγραφής στον πίνακα Car
            cursor.execute("DELETE FROM Car WHERE car_id = ?", (car_id,))

            if cursor.rowcount > 0:
                print(">> Το αυτοκίνητο διαγράφηκε επιτυχώς.")
            else:
                print(">> Δεν βρέθηκε αυτοκίνητο με αυτό το ID.")

    except sqlite3.IntegrityError:
        # Σφάλμα που προκύπτει λόγω ON DELETE RESTRICT
        print(">> Σφάλμα: Το αυτοκίνητο δεν μπορεί να διαγραφεί γιατί συνδέεται με υπάρχουσες κρατήσεις.")
    except Exception as e:
        print(f">> Προέκυψε σφάλμα: {e}")
    finally:
        conn.close()


def create_reservation():
    print("\n--- Νέα Κράτηση ---")
    cust_id = int(input("ID Πελάτη: "))
    car_id = int(input("ID Αυτοκινήτου: "))
    p_date = input("Παραλαβή (YYYY-MM-DD): ")
    d_date = input("Παράδοση (YYYY-MM-DD): ")
    p_loc = int(input("ID Τοποθεσίας Παραλαβής: "))
    d_loc = int(input("ID Τοποθεσίας Παράδοσης: "))
    ins_id = int(input("ID Ασφάλειας: "))
    cat_id = int(input("ID Κατηγορίας: "))

    conn = get_connection()
    try:
        with conn:
            query = """INSERT INTO Reservation (pick_up_date, drop_off_date, car_id, pick_up_location,
                                                drop_off_location, customer_id, insurance_preference, category_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            conn.execute(query, (p_date, d_date, car_id, p_loc, d_loc, cust_id, ins_id, cat_id))
        print(">> Η κράτηση δημιουργήθηκε[cite: 2, 21]!")
    finally:
        conn.close()


def read_reservations():
    """Προβολή όλων των κρατήσεων με ονόματα πελατών και αυτοκινήτων."""
    print("\n--- Λίστα Κρατήσεων ---")
    conn = get_connection()
    cursor = conn.cursor()

    # Χρησιμοποιούμε JOIN για να πάρουμε το όνομα του πελάτη και τη μάρκα/μοντέλο του αυτοκινήτου
    query = """
            SELECT r.reservation_id, \
                   c.full_name, \
                   car.brand, \
                   car.model, \
                   r.pick_up_date, \
                   r.drop_off_date
            FROM Reservation r
                     JOIN Customer c ON r.customer_id = c.customer_id
                     JOIN Car car ON r.car_id = car.car_id \
            """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("Δεν υπάρχουν καταχωρημένες κρατήσεις.")
        else:
            for row in rows:
                print(f"ID: {row[0]} | Πελάτης: {row[1]} | Αυτοκίνητο: {row[2]} {row[3]} | Από: {row[4]} Έως: {row[5]}")
    except Exception as e:
        print(f">> Σφάλμα κατά την ανάγνωση των κρατήσεων: {e}")
    finally:
        conn.close()

def read_payments():
    conn = get_connection()
    cursor = conn.cursor()
    # Εμφανίζει το συνολικό ποσό ανά κράτηση και πελάτη
    query = """SELECT p.payment_number, p.total_amount, c.full_name, p.reservation_id
               FROM Payment p \
                        JOIN Customer c ON p.customer_id = c.customer_id"""
    cursor.execute(query)
    print("\n--- Λίστα Πληρωμών ---")
    for row in cursor.fetchall():
        print(f"Πληρωμή #{row[0]} | Ποσό: {row[1]}€ | Πελάτης: {row[2]} | Κράτηση: {row[3]}")
    conn.close()


def create_pickup_dropoff(type):
    table = "PickUp" if type == "P" else "DropOff"
    state_col = "pick_up_state" if type == "P" else "drop_off_state"
    date_col = "true_pick_up_date" if type == "P" else "true_drop_off_date"

    print(f"\n--- Καταγραφή {table} ---")
    res_id = int(input("ID Κράτησης: "))
    emp_id = int(input("ID Υπαλλήλου: "))
    loc_id = int(input("ID Τοποθεσίας: "))
    state = input("Κατάσταση Οχήματος: ")
    date = input("Ημερομηνία/Ώρα: ")

    conn = get_connection()
    try:
        with conn:
            query = f"INSERT INTO {table} (employee_id, reservation_id, location_id, {state_col}, {date_col}) VALUES (?,?,?,?,?)"
            conn.execute(query, (emp_id, res_id, loc_id, state, date))
        print(f">> Η καταγραφή {table} ολοκληρώθηκε[cite: 20, 30]!")
    finally:
        conn.close()

def read_pickups():
    """Προβολή όλων των καταγεγραμμένων παραλαβών."""
    print("\n--- Ιστορικό Παραλαβών (PickUp) ---")
    conn = get_connection()
    cursor = conn.cursor()
    # Σύνδεση PickUp με Employee για να βλέπουμε το επώνυμο του υπαλλήλου
    query = """
    SELECT p.pick_up_id, p.reservation_id, e.surname, p.pick_up_state, p.true_pick_up_date
    FROM PickUp p
    JOIN Employee e ON p.employee_id = e.employee_id
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            print("Δεν υπάρχουν καταγεγραμμένες παραλαβές.")
        else:
            for row in rows:
                print(f"ID: {row[0]} | Κράτηση: {row[1]} | Υπάλληλος: {row[2]} | Κατάσταση: {row[3]} | Ημερ: {row[4]}")
    except Exception as e:
        print(f">> Σφάλμα κατά την ανάγνωση των PickUp: {e}")
    finally:
        conn.close()

def read_dropoffs():
    """Προβολή όλων των καταγεγραμμένων παραδόσεων."""
    print("\n--- Ιστορικό Παραδόσεων (DropOff) ---")
    conn = get_connection()
    cursor = conn.cursor()
    # Σύνδεση DropOff με Employee
    query = """
    SELECT d.drop_off_id, d.reservation_id, e.surname, d.drop_off_state, d.true_drop_off_date
    FROM DropOff d
    JOIN Employee e ON d.employee_id = e.employee_id
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            print("Δεν υπάρχουν καταγεγραμμένες παραδόσεις.")
        else:
            for row in rows:
                print(f"ID: {row[0]} | Κράτηση: {row[1]} | Υπάλληλος: {row[2]} | Κατάσταση: {row[3]} | Ημερ: {row[4]}")
    except Exception as e:
        print(f">> Σφάλμα κατά την ανάγνωση των DropOff: {e}")
    finally:
        conn.close()

def create_employee():
    print("\n--- Προσθήκη Νέου Υπαλλήλου ---")
    name = input("Όνομα: ")
    surname = input("Επώνυμο: ")
    email = input("Email (πρέπει να είναι μοναδικό): ")
    phone = input("Τηλέφωνο: ")
    afm = input("ΑΦΜ: ")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Σύμφωνα με τη δομή: name, surname, email, phone, afm
            query = """INSERT INTO Employee (name, surname, email, phone, afm)
                       VALUES (?, ?, ?, ?, ?)"""
            cursor.execute(query, (name, surname, email, phone, afm))
        print(f">> Ο υπάλληλος {surname} προστέθηκε επιτυχώς!")
    except sqlite3.IntegrityError:
        print(">> Σφάλμα: Το email ή το ΑΦΜ υπάρχει ήδη στη βάση.")
    except Exception as e:
        print(f">> Σφάλμα: {e}")
    finally:
        conn.close()


def read_employees():
    print("\n--- Λίστα Υπαλλήλων ---")
    conn = get_connection()
    cursor = conn.cursor()
    # Ανάκτηση βασικών στοιχείων υπαλλήλων [cite: 7]
    cursor.execute("SELECT employee_id, name, surname, email, phone FROM Employee")
    rows = cursor.fetchall()

    if not rows:
        print("Δεν βρέθηκαν υπάλληλοι.")
    for row in rows:
        print(f"ID: {row[0]} | {row[1]} {row[2]} | Email: {row[3]} | Τηλ: {row[4]}")
    conn.close()


def update_employee_contact():
    """Ενημέρωση τηλεφώνου ή email υπαλλήλου."""
    read_employees()
    emp_id = input("\nΕισάγετε το ID του υπαλλήλου για ενημέρωση: ")
    print("1. Αλλαγή Τηλεφώνου | 2. Αλλαγή Email")
    choice = input("Επιλογή: ")

    field = "phone" if choice == '1' else "email"
    new_val = input(f"Εισάγετε το νέο {field}: ")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Employee SET {field} = ? WHERE employee_id = ?", (new_val, emp_id))
            if cursor.rowcount > 0:
                print(">> Τα στοιχεία ενημερώθηκαν!")
            else:
                print(">> Δεν βρέθηκε υπάλληλος με αυτό το ID.")
    finally:
        conn.close()


def delete_employee():
    read_employees()
    emp_id = input("\nΕισάγετε το ID του υπαλλήλου προς διαγραφή: ")
    conn = get_connection()
    try:
        with conn:
            # Η διαγραφή περιορίζεται αν ο υπάλληλος έχει καταγραφεί σε PickUp ή DropOff
            conn.execute("DELETE FROM Employee WHERE employee_id = ?", (emp_id,))
        print(">> Ο υπάλληλος διαγράφηκε.")
    except sqlite3.IntegrityError:
        print(">> Σφάλμα: Ο υπάλληλος δεν μπορεί να διαγραφεί (έχει καταγραφές παραλαβών/παραδόσεων).")
    finally:
        conn.close()


def create_insurance_plan():
    print("\n--- Προσθήκη Νέου Ασφαλιστικού Πλάνου ---")
    try:
        price = int(input("Εισάγετε την τιμή του πλάνου: "))

        conn = get_connection()
        with conn:
            cursor = conn.cursor()
            # Ο πίνακας InsurancePlan έχει τη στήλη insurance_price
            query = "INSERT INTO InsurancePlan (insurance_price) VALUES (?)"
            cursor.execute(query, (price,))
        print(f">> Το πλάνο με τιμή {price}€ προστέθηκε επιτυχώς!")
    except ValueError:
        print(">> Σφάλμα: Παρακαλώ εισάγετε έναν έγκυρο αριθμό για την τιμή.")
    except Exception as e:
        print(f">> Σφάλμα: {e}")
    finally:
        conn.close()


def read_insurance_plans():
    print("\n--- Διαθέσιμα Ασφαλιστικά Πλάνα ---")
    conn = get_connection()
    cursor = conn.cursor()
    # Ανάκτηση των πεδίων plan_id και insurance_price
    cursor.execute("SELECT plan_id, insurance_price FROM InsurancePlan")
    rows = cursor.fetchall()

    if not rows:
        print("Δεν βρέθηκαν ασφαλιστικά πλάνα.")
    for row in rows:
        print(f"ID Πλάνου: {row[0]} | Τιμή: {row[1]}€")
    conn.close()


def update_insurance_price():
    read_insurance_plans()
    plan_id = input("\nΕισάγετε το ID του πλάνου για ενημέρωση τιμής: ")
    try:
        new_price = int(input("Νέα Τιμή: "))

        conn = get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE InsurancePlan SET insurance_price = ? WHERE plan_id = ?", (new_price, plan_id))
            if cursor.rowcount > 0:
                print(">> Η τιμή του πλάνου ενημερώθηκε!")
            else:
                print(">> Δεν βρέθηκε πλάνο με αυτό το ID.")
    except ValueError:
        print(">> Σφάλμα: Η τιμή πρέπει να είναι αριθμός.")
    finally:
        conn.close()


def delete_insurance_plan():
    read_insurance_plans()
    plan_id = input("\nΕισάγετε το ID του πλάνου προς διαγραφή: ")
    conn = get_connection()
    try:
        with conn:
            # Η διαγραφή θα αποτύχει αν το πλάνο χρησιμοποιείται στον πίνακα Reservation
            conn.execute("DELETE FROM InsurancePlan WHERE plan_id = ?", (plan_id,))
        print(">> Το ασφαλιστικό πλάνο διαγράφηκε.")
    except sqlite3.IntegrityError:
        print(">> Σφάλμα: Το πλάνο δεν μπορεί να διαγραφεί (χρησιμοποιείται σε υπάρχουσες κρατήσεις).")
    finally:
        conn.close()


def create_category():
    print("\n--- Προσθήκη Νέας Κατηγορίας ---")
    name = input("Όνομα Κατηγορίας (π.χ. SUV, Mini Van): ")
    try:
        # Το πεδίο vehicle_count ορίζεται ως INTEGER στη βάση σας
        count = int(input("Αριθμός Οχημάτων στην κατηγορία: "))

        conn = get_connection()
        with conn:
            cursor = conn.cursor()
            query = "INSERT INTO Category (category_name, vehicle_count) VALUES (?, ?)"
            cursor.execute(query, (name, count))
        print(f">> Η κατηγορία '{name}' προστέθηκε επιτυχώς!")
    except ValueError:
        print(">> Σφάλμα: Ο αριθμός οχημάτων πρέπει να είναι ακέραιος.")
    finally:
        conn.close()


def read_categories():
    print("\n--- Λίστα Κατηγοριών ---")
    conn = get_connection()
    cursor = conn.cursor()
    # Ανάκτηση των πεδίων category_id, category_name και vehicle_count
    cursor.execute("SELECT category_id, category_name, vehicle_count FROM Category")
    rows = cursor.fetchall()

    if not rows:
        print("Δεν βρέθηκαν κατηγορίες.")
    else:
        for row in rows:
            print(f"ID: {row[0]} | Όνομα: {row[1]} | Πλήθος Οχημάτων: {row[2]}")
    conn.close()


def update_category_details():
    """Ενημέρωση του ονόματος ή του αριθμού οχημάτων της κατηγορίας."""
    read_categories()
    cat_id = input("\nΕισάγετε το ID της κατηγορίας για ενημέρωση: ")
    print("1. Αλλαγή Ονόματος | 2. Αλλαγή Πλήθους Οχημάτων")
    choice = input("Επιλογή (1-2): ")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            if choice == '1':
                new_name = input("Νέο Όνομα: ")
                cursor.execute("UPDATE Category SET category_name = ? WHERE category_id = ?", (new_name, cat_id))
            elif choice == '2':
                new_count = int(input("Νέο Πλήθος Οχημάτων: "))
                cursor.execute("UPDATE Category SET vehicle_count = ? WHERE category_id = ?", (new_count, cat_id))

            if cursor.rowcount > 0:
                print(">> Η κατηγορία ενημερώθηκε!")
            else:
                print(">> Δεν βρέθηκε κατηγορία με αυτό το ID.")
    except ValueError:
        print(">> Σφάλμα: Παρακαλώ εισάγετε έγκυρα δεδομένα.")
    finally:
        conn.close()


def delete_category():
    read_categories()
    cat_id = input("\nΕισάγετε το ID της κατηγορίας προς διαγραφή: ")
    conn = get_connection()
    try:
        with conn:
            # Η διαγραφή περιορίζεται αν η κατηγορία συνδέεται με αυτοκίνητα ή κρατήσεις
            conn.execute("DELETE FROM Category WHERE category_id = ?", (cat_id,))
        print(">> Η κατηγορία διαγράφηκε επιτυχώς.")
    except sqlite3.IntegrityError:
        print(">> Σφάλμα: Η κατηγορία χρησιμοποιείται από αυτοκίνητα ή κρατήσεις και δεν μπορεί να διαγραφεί.")
    finally:
        conn.close()

def show_statistics():
    """Εμφάνιση βασικών στατιστικών στοιχείων από τη βάση."""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 40)
    print("   ΣΥΝΟΠΤΙΚΑ ΣΤΑΤΙΣΤΙΚΑ ΕΠΙΧΕΙΡΗΣΗΣ")
    print("=" * 40)

    # 1. Συνολικά Έσοδα από τον πίνακα Payment
    cursor.execute("SELECT SUM(total_amount) FROM Payment")
    total_revenue = cursor.fetchone()[0]
    print(f"1. Συνολικά Έσοδα: {total_revenue if total_revenue else 0}€")

    # 2. Κατάσταση Στόλου από τον πίνακα Car
    cursor.execute("SELECT COUNT(*) FROM Car WHERE availability = 1")
    avail = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Car WHERE availability = 0")
    rented = cursor.fetchone()[0]
    print(f"2. Κατάσταση Στόλου: {avail} Διαθέσιμα / {rented} Νοικιασμένα")

    # 3. Δημοφιλέστερες Κατηγορίες (σύνδεση Category & Reservation) [cite: 8, 27]
    print("\n3. Κρατήσεις ανά Κατηγορία:")
    query_cat = """
                SELECT c.category_name, COUNT(r.reservation_id) as res_count
                FROM Category c
                         LEFT JOIN Reservation r ON c.category_id = r.category_id
                GROUP BY c.category_id
                ORDER BY res_count DESC \
                """
    cursor.execute(query_cat)
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]} κρατήσεις")

    conn.close()


def show_advanced_report():
    """
    Το πιο σύνθετο query: Αναλυτική αναφορά που συνδέει 5 πίνακες:
    Reservation, Customer, Car, Category και Payment.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            SELECT r.reservation_id, \
                   c.full_name, \
                   car.brand || ' ' || car.model AS vehicle, \
                   cat.category_name, \
                   p.total_amount
            FROM Reservation r
                     JOIN Customer c ON r.customer_id = c.customer_id
                     JOIN Car car ON r.car_id = car.car_id
                     JOIN Category cat ON r.category_id = cat.category_id
                     LEFT JOIN Payment p ON r.reservation_id = p.reservation_id \
            """

    print("\n" + "=" * 70)
    print(f"{'ID':<4} | {'ΠΕΛΑΤΗΣ':<20} | {'ΟΧΗΜΑ':<15} | {'ΚΑΤΗΓΟΡΙΑ':<12} | {'ΠΟΣΟ'}")
    print("-" * 70)

    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("Δεν βρέθηκαν δεδομένα για αναφορά.")
    else:
        for row in rows:
            amount = f"{row[4]}€" if row[4] is not None else "Εκκρεμεί"
            print(f"{row[0]:<4} | {row[1]:<20} | {row[2]:<15} | {row[3]:<12} | {amount}")

    conn.close()

def main():
    while True:
        print("\n" + "=" * 60)
        print("   ΣΥΣΤΗΜΑ ΔΙΑΧΕΙΡΙΣΗΣ ΕΦΑΡΜΟΓΗΣ ΕΝΟΙΚΙΑΣΗΣ ΑΥΤΟΚΙΝΗΤΩΝ")
        print("=" * 60)
        print("1. ΔΙΑΧΕΙΡΙΣΗ ΠΕΛΑΤΩΝ")
        print("2. ΔΙΑΧΕΙΡΙΣΗ ΑΥΤΟΚΙΝΗΤΩΝ")
        print("3. ΔΙΑΧΕΙΡΙΣΗ ΚΡΑΤΗΣΕΩΝ")
        print("4. ΚΑΤΑΛΟΓΟΣ ΠΛΗΡΩΜΩΝ")
        print("5. ΠΑΡΑΛΑΒΗ & ΠΑΡΑΔΟΣΗ (PickUp/DropOff)")
        print("6. ΥΠΑΛΛΗΛΟΙ")
        print("7. ΑΣΦΑΛΙΣΤΙΚΑ ΠΛΑΝΑ")
        print("8. ΚΑΤΗΓΟΡΙΕΣ ΑΥΤΟΚΙΝΗΤΩΝ")
        print("9. ΣΤΑΤΙΣΤΙΚΑ")
        print("10. ΕΞΟΔΟΣ")

        choice = input("Επιλέξτε κατηγορία (1-10): ")

        if choice == '1':
            print("\n[ΠΕΛΑΤΕΣ] 1.Λίστα 2.Προσθήκη 3.Ενημέρωση Στοιχείων 4.Διαγραφή")
            sub = input("Επιλογή: ")
            if sub == '1':
                read_customers()
            elif sub == '2':
                create_customer()
            elif sub == '3':
                update_customer()
            elif sub == '4':
                delete_customer()

        elif choice == '2':
            print("\n[ΑΥΤΟΚΙΝΗΤΑ] 1.Λίστα 2.Προσθήκη 3.Ενημέρωση Τιμής 4.Διαγραφή")
            sub = input("Επιλογή: ")
            if sub == '1':
                read_cars()
            elif sub == '2':
                create_car()
            elif sub == '3':
                update_car_price()
            elif sub == '4':
                delete_car()

        elif choice == '3':
            print("\n[ΚΡΑΤΗΣΕΙΣ] 1.Προβολή 2.Νέα Κράτηση")
            sub = input("Επιλογή: ")
            if sub == '1':
                read_reservations()
            elif sub == '2':
                create_reservation()

        elif choice == '4':
            read_payments()  # Read operation για Payment [cite: 2, 29]

        elif choice == '5':
            print("\n[P/D] 1.Λίστα PickUp 2.Νέο PickUp 3.Λίστα DropOff 4.Νέο DropOff")
            sub = input("Επιλογή: ")
            if sub == '1':
                read_pickups()
            elif sub == '2':
                create_pickup_dropoff("P")
            elif sub == '3':
                read_dropoffs()
            elif sub == '4':
                create_pickup_dropoff("D")

        elif choice == '6':
            print("\n[ΥΠΑΛΛΗΛΟΙ] 1.Λίστα 2.Προσθήκη 3.Ενημέρωση 4.Διαγραφή")
            sub = input("Επιλογή: ")
            if sub == '1':
                read_employees()
            elif sub == '2':
                create_employee()
            elif sub == '3':
                update_employee_contact()
            elif sub == '4':
                delete_employee()

        elif choice == '7':  # Υποθετική νέα επιλογή στο μενού
            print("\n[ΑΣΦΑΛΕΙΑ] 1.Λίστα 2.Προσθήκη 3.Ενημέρωση Τιμής 4.Διαγραφή")
            sub = input("Επιλογή: ")
            if sub == '1':
                read_insurance_plans()
            elif sub == '2':
                create_insurance_plan()
            elif sub == '3':
                update_insurance_price()
            elif sub == '4':
                delete_insurance_plan()

        elif choice == '8':
            print("\n[ΚΑΤΗΓΟΡΙΕΣ] 1.Λίστα 2.Προσθήκη 3.Ενημέρωση 4.Διαγραφή")
            sub = input("Επιλογή: ")
            if sub == '1':
                read_categories()
            elif sub == '2':
                create_category()
            elif sub == '3':
                update_category_details()
            elif sub == '4':
                delete_category()

        elif choice == '9':
            show_statistics()
            show_advanced_report()

        elif choice == '10':
            print("Τερματισμός εφαρμογής...")
            break
        else:
            print("Μη έγκυρη επιλογή, προσπαθήστε ξανά.")


if __name__ == "__main__":
    create_indexes()
    main()
