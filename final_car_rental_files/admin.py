import os
import datetime

# -----------------------------------------------------------------------------
# UTILITIES & INPUT HANDLING
# -----------------------------------------------------------------------------

def clear_screen():
    print("\n" * 2)
    print("=" * 60)
    print("\n")

def get_input(prompt_text):
    val = input(f"{prompt_text} [q to cancel]: ").strip()
    if val.lower() == 'q':
        print(">> Operation Cancelled by user.")
        return None
    return val

def get_int(prompt_text):
    while True:
        val = input(f"{prompt_text} [q to cancel]: ").strip()
        if val.lower() == 'q':
            print(">> Operation Cancelled.")
            return None
        try:
            return int(val)
        except ValueError:
            print("!! Error: Please enter a valid number (integer).")

def print_result(success, result):
    """
    Displays the outcome of a database operation.
    """
    if success:
        if result is None:
            print(">> Success: Operation Completed.")
        else:
            print(f">> Success: Operation Completed (ID: {result})")
    else:
        print(f"!! Error: {result}")


# -----------------------------------------------------------------------------
# MAIN APPLICATION LOGIC
# -----------------------------------------------------------------------------

def run_admin_interface(model):
    try:
        model.create_indexes()
    except Exception:
        pass 

    while True:
        clear_screen()
        print("                  ADMINISTRATIVE CONSOLE      ")
        print("=" * 60)
        print("1. Manage Customers")
        print("2. Manage Fleet (Cars)")
        print("3. Manage Reservations")
        print("4. Manage Employees")
        print("5. View Reports & Intelligence")
        print("6. Operations Log (PickUp / DropOff)")
        print("7. EXIT SYSTEM")
        print("=" * 60)

        choice = input("\nEnter Selection (1-7): ").strip()

        if choice == '1':
            menu_customers(model)
        elif choice == '2':
            menu_cars(model)
        elif choice == '3':
            menu_reservations(model)
        elif choice == '4':
            menu_employees(model)
        elif choice == '5':
            menu_reports(model)
        elif choice == '6':
            menu_operations(model)
        elif choice == '7' or choice.lower() == 'q':
            print("Exiting Admin Console... Goodbye!")
            break
        else:
            print("Invalid selection. Please try again.")
            input("Press Enter to continue...")


# -----------------------------------------------------------------------------
# 1. CUSTOMER MANAGEMENT
# -----------------------------------------------------------------------------

def menu_customers(model):
    while True:
        clear_screen()
        print("--- CUSTOMER MANAGEMENT ---")
        print("1. View All Customers")
        print("2. Add New Customer")
        print("3. Update Customer Details")
        print("4. Delete Customer")
        print("5. < BACK")
        
        sel = input("\nSelect Action: ").strip()

        if sel == '1':
            success, rows = model.get_all_customers()
            if success and rows:
                print(f"\n{'ID':<5} {'NAME':<25} {'EMAIL':<30} {'PHONE'}")
                print("-" * 75)
                for r in rows:
                    cid = str(r.get('customer_id', 'N/A'))
                    name = r.get('full_name', r.get('name', 'N/A'))
                    email = r.get('email', 'N/A')
                    phone = r.get('phone', r.get('phone_number', 'N/A'))
                    
                    # Truncate fields to ensure alignment
                    print(f"{cid:<5} {name[:24]:<25} {email[:29]:<30} {phone}")
            else:
                print("\nNo customers found or database error.")
            input("\nPress Enter to return...")

        elif sel == '2':
            print("\n>> ADDING NEW CUSTOMER")
            name = get_input("Full Name")
            if not name: continue
            
            email = get_input("Email Address")
            if not email: continue
            
            phone = get_input("Phone Number")
            if not phone: continue
            
            license_id = get_input("Driver's License ID")
            if not license_id: continue
            
            address = get_input("Home Address")
            if not address: continue
            
            dob = get_input("Date of Birth (YYYY-MM-DD)")
            if not dob: continue

            data = {
                'name': name, 'email': email, 'phone': phone, 
                'license': license_id, 'address': address, 'dob': dob
            }
            success, result = model.add_customer(data)
            print_result(success, result)
            input("Press Enter...")

        elif sel == '3':
            cid = get_int("Enter Customer ID to update")
            if not cid: continue
            
            print("Fields: 1.Phone  2.Email")
            field_choice = input("Select Field: ")
            
            if field_choice == '1':
                val = get_input("New Phone Number")
                if val: print_result(*model.update_customer(cid, "phone", val))
            elif field_choice == '2':
                val = get_input("New Email Address")
                if val: print_result(*model.update_customer(cid, "email", val))
            input("Press Enter...")

        elif sel == '4':
            cid = get_int("Enter Customer ID to DELETE")
            if not cid: continue
            
            if input(f"Delete ID {cid}? (yes/no): ").lower() == 'yes':
                print_result(*model.delete_customer(cid))
            input("Press Enter...")

        elif sel == '5' or sel.lower() == 'q':
            return


# -----------------------------------------------------------------------------
# 2. FLEET (CAR) MANAGEMENT
# -----------------------------------------------------------------------------

def menu_cars(model):
    while True:
        clear_screen()
        print("--- FLEET MANAGEMENT ---")
        print("1. View All Cars")
        print("2. Add New Car")
        print("3. Update Car Price")
        print("4. Retire Car (Make Unavailable)")
        print("5. Reactivate Car (Make Available)")
        print("6. Update Mileage")  
        print("7. < BACK")

        sel = input("\nSelect Action: ").strip()

        if sel == '1':
            success, rows = model.get_all_cars()
            if success and rows:
                print(f"\n{'ID':<5} {'MODEL':<20} {'PLATE':<10} {'PRICE':<8} {'MIL':<8} {'STATUS'}")
                print("-" * 65)
                for r in rows:
                    status = "Active" if r.get('availability', 1) == 1 else "Retired"
                    cid = str(r.get('car_id', 'N/A'))
                    
                    brand = r.get('brand', '')
                    model_n = r.get('model', '')
                    full_model = f"{brand} {model_n}"

                    plate = r.get('plate', r.get('plate_id', 'N/A'))
                    price = str(r.get('price_per_day', 'N/A'))
                    mil = str(r.get('mileage', '0'))
                    
                    print(f"{cid:<5} {full_model[:19]:<20} {plate:<10} {price:<8} {mil:<8} {status}")
            else:
                print("No cars found.")
            input("\nPress Enter...")

        elif sel == '2':
            print("\n>> ADD NEW CAR")
            plate = get_input("License Plate")
            if not plate: continue
            
            brand = get_input("Brand (Make)")
            if not brand: continue
            
            model_n = get_input("Model")
            if not model_n: continue
            
            price = get_int("Daily Price (EUR)")
            if not price: continue
            
            color = get_input("Color")
            gear = get_input("Gearbox (Manual/Automatic)")
            mil = get_int("Current Mileage (km)")
            loc_id = get_int("Location ID")
            cat_id = get_int("Category ID")
            
            if not all([color, gear, mil, loc_id, cat_id]): continue
            
            data = {
                'plate': plate, 'brand': brand, 'model': model_n, 'price': price, 
                'color': color, 'gear': gear, 'mil': mil, 'loc_id': loc_id, 'cat_id': cat_id
            }
            print_result(*model.add_car(data))
            input("Press Enter...")

        elif sel == '3':
            cid = get_int("Car ID")
            if not cid: continue
            new_price = get_int("New Price")
            if new_price: print_result(*model.update_car_price(cid, new_price))
            input("Press Enter...")

        elif sel == '4':
            cid = get_int("Car ID to Retire")
            if cid: 
                success, msg = model.retire_car(cid)
                if success:
                    print(f">> Success: Car #{cid} retired.")
                else:
                    print(f"!! Failed: {msg}")
            input("Press Enter...")

        elif sel == '5':
            cid = get_int("Car ID to Reactivate")
            if cid: print_result(*model.activate_car(cid))
            input("Press Enter...")
        
        elif sel == '6':
            cid = get_int("Car ID to Update")
            if not cid: continue
            new_mil = get_int("New Mileage (km)")
            if new_mil: print_result(*model.update_car_mileage(cid, new_mil))
            input("Press Enter...")

        elif sel == '7' or sel.lower() == 'q':
            return


# -----------------------------------------------------------------------------
# 3. RESERVATIONS
# -----------------------------------------------------------------------------

def menu_reservations(model):
    while True:
        clear_screen()
        print("--- RESERVATIONS ---")
        print("1. View All History")
        print("2. View Active / Future Only")
        print("3. Create New Reservation")
        print("4. Cancel Reservation (Soft Delete)")
        print("5. < BACK")

        sel = input("\nSelect Action: ").strip()

        if sel == '1':
            s, rows = model.get_all_reservations()
            if s and rows:
                print(f"\n{'ID':<5} {'CUSTOMER':<20} {'CAR':<20} {'STATUS':<12} {'DATES'}")
                print("-" * 80)
                for r in rows:
                    rid = str(r.get('reservation_id', 'N/A'))
                    name = r.get('full_name', 'N/A')
                    car = f"{r.get('brand','')} {r.get('model','')}"
                    p_date = str(r.get('pick_up_date', ''))
                    d_date = str(r.get('drop_off_date', ''))
                    dates = f"{p_date} -> {d_date}"
                    status = r.get('status', 'Confirmed') 
                    
                    print(f"#{rid:<4} {name[:19]:<20} {car[:19]:<20} {status:<12} {dates}")
            else:
                if not s:
                    print(f"\n❌ DATABASE ERROR: {rows}")
                else:
                    print("\nNo reservations found (List is empty).")
            input("\nPress Enter...")
        
        elif sel == '2':
            s, rows = model.get_active_future_reservations()
            if s and rows:
                print("\n>>> ACTIVE & UPCOMING BOOKINGS <<<")
                print(f"{'ID':<5} {'CUSTOMER':<20} {'CAR':<20} {'STATUS':<12} {'PICK-UP'}")
                print("-" * 80)
                for r in rows:
                    rid = str(r.get('reservation_id', 'N/A'))
                    name = r.get('full_name', 'N/A')
                    car = f"{r.get('brand','')} {r.get('model','')}"
                    p_date = str(r.get('pick_up_date', ''))
                    status = r.get('status', 'Confirmed')
                    
                    print(f"#{rid:<4} {name[:19]:<20} {car[:19]:<20} {status:<12} {p_date}")
            else:
                print("No active or future reservations found.")
            input("\nPress Enter...")

        elif sel == '3':
            cust_id = get_int("Customer ID")
            car_id = get_int("Car ID")
            if not cust_id or not car_id: continue
            
            p_date = get_input("Pickup (YYYY-MM-DD)")
            d_date = get_input("Dropoff (YYYY-MM-DD)")
            p_loc = get_int("Pickup Loc ID")
            d_loc = get_int("Dropoff Loc ID")
            ins_id = get_int("Ins ID (0/1)")
            cat_id = get_int("Cat ID")
            
            if all([p_date, d_date, p_loc, d_loc]):
                data = {
                    'cust_id': cust_id, 'car_id': car_id, 'p_date': p_date, 'd_date': d_date, 
                    'p_loc': p_loc, 'd_loc': d_loc, 'ins_id': ins_id, 'cat_id': cat_id
                }
                print_result(*model.add_reservation(data))
            input("Press Enter...")

        elif sel == '4':
            print("\n--- CANCEL RESERVATION ---")
            r_id = get_input("Enter Reservation ID to cancel")
            if r_id:
                confirm = input(f"Mark Reservation #{r_id} as Cancelled? (y/n): ")
                if confirm.lower() == 'y':
                    print_result(*model.cancel_reservation(r_id))
                else:
                    print("Operation cancelled.")
            input("Press Enter...")

        elif sel == '5' or sel.lower() == 'q':
            return


# -----------------------------------------------------------------------------
# 4. EMPLOYEES 
# -----------------------------------------------------------------------------

def menu_employees(model):
    while True:
        clear_screen()
        print("--- EMPLOYEE MANAGEMENT ---")
        print("1. View Staff Directory")
        print("2. View Employee Work History")
        print("3. Add Employee")
        print("4. Remove Employee")
        print("5. < BACK")

        sel = input("\nAction: ").strip()

        if sel == '1':
            s, rows = model.get_all_employees()
            if s and rows:
                print(f"\n{'ID':<5} {'NAME':<20} {'EMAIL'}")
                print("-" * 50)
                for r in rows:
                    eid = r.get('employee_id', 'N/A')
                    name = f"{r.get('name', '')} {r.get('surname', '')}"
                    email = r.get('email', 'N/A')
                    print(f"#{eid:<4} {name[:19]:<20} {email}")
            else:
                print("No employees found.")
            input("Press Enter...")

        elif sel == '2':
            eid = get_int("Enter Employee ID")
            if eid:
                s, rows = model.get_employee_work_history(eid)
                if s and rows:
                    print(f"\n--- WORK LOG FOR EMP #{eid} ---")
                    print(f"{'RES ID':<8} {'ACTION':<10} {'DATE'}")
                    print("-" * 40)
                    for r in rows:
                        print(f"#{r['reservation_id']:<7} {r['type']:<10} {r['action_date']}")
                else:
                    print("No work history found for this ID.")
            input("Press Enter...")

        elif sel == '3':
            data = {}
            data['name'] = get_input("First Name")
            data['surname'] = get_input("Surname")
            data['email'] = get_input("Email")
            data['phone'] = get_input("Phone")
            data['afm'] = get_input("Tax ID (AFM)")
            
            if all(data.values()): 
                print_result(*model.add_employee(data))
            input("Press Enter...")

        elif sel == '4':
            eid = get_int("Employee ID")
            if eid: 
                print_result(*model.delete_employee(eid))
            input("Press Enter...")
        
        elif sel == '5' or sel.lower() == 'q':
            return


# -----------------------------------------------------------------------------
# 5. REPORTS 
# -----------------------------------------------------------------------------

def menu_reports(model):
    while True:
        clear_screen()
        print("--- REPORTS & INTELLIGENCE ---")
        print("1. Payments Log")
        print("2. Financial Stats")
        print("3. Store Popularity")
        print("4. VIP Customers")
        print("5. Avg Rental Duration")
        print("6. < BACK")

        sel = input("\nSelect: ").strip()

        if sel == '1':
            s, rows = model.get_all_payments()
            if s and rows:
                print(f"\n{'ID':<10} {'AMOUNT':<10} {'CUSTOMER'}")
                print("-" * 50)
                for r in rows:
                    pid = str(r.get('payment_id', r.get('payment_number', 'N/A')))
                    amt = str(r.get('amount', r.get('total_amount', '0')))
                    name = r.get('full_name', 'N/A')
                    print(f"{pid:<10} {amt:<10} {name}")
            else:
                print("No payments found.")
            input("\nPress Enter...")
        
        elif sel == '2':
            try:
                stats = model.get_stats()
                print(f"\nTotal Revenue: {stats.get('revenue', 0)} EUR")
                print(f"Fleet Status:  {stats.get('avail', 0)} Available / {stats.get('rented', 0)} Rented")
            except Exception as e:
                print(f"Error retrieving stats: {e}")
            input("Press Enter...")

        elif sel == '3':
            try:
                s, data = model.get_most_popular_store()
                if s and data:
                    print("\n🏆 MOST POPULAR LOCATION 🏆")
                    print(f"Address:  {data['address']}")
                    print(f"Pick-Ups: {data['usage_count']}")
                else:
                    print("Not enough data.")
            except Exception as e:
                print(f"Error: {e}")
            input("Press Enter...")

        elif sel == '4':
            try:
                if hasattr(model, 'get_top_customers'):
                    s, rows = model.get_top_customers()
                    if s and rows:
                        print("\n--- TOP SPENDERS ---")
                        for i, r in enumerate(rows, 1):
                            name = r.get('full_name', 'N/A')
                            spent = r.get('spent', r.get('total_spent', 0))
                            print(f"{i}. {name} - {spent} EUR")
                    else:
                        print("No data.")
            except:
                pass
            input("Press Enter...")
        
        elif sel == '5':
            try:
                if hasattr(model, 'get_avg_duration'):
                    print(f"\nAvg Rental Duration: {model.get_avg_duration()} Days")
            except:
                pass
            input("Press Enter...")
        
        elif sel == '6' or sel.lower() == 'q':
            return


# -----------------------------------------------------------------------------
# 6. OPERATIONS LOGGING
# -----------------------------------------------------------------------------

def menu_operations(model):
    while True:
        clear_screen()
        print("--- OPERATIONS LOG ---")
        print("1. View PickUp Log")
        print("2. View DropOff Log")
        print("3. Log PickUp Action")
        print("4. Log DropOff Action")
        print("5. < BACK")

        sel = input("\nAction: ").strip()

        if sel == '1':
            s, rows = model.get_pickups_dropoffs("PickUp")
            if s and rows:
                for r in rows:
                    print(f"LOG #{r['id']} | RES #{r['reservation_id']} | Status: {r.get('state', 'N/A')}")
            else:
                print("No Pickup logs found.")
            input("Press Enter...")

        elif sel == '2':
            s, rows = model.get_pickups_dropoffs("DropOff")
            if s and rows:
                for r in rows:
                    print(f"LOG #{r['id']} | RES #{r['reservation_id']} | Status: {r.get('state', 'N/A')}")
            else:
                print("No Dropoff logs found.")
            input("Press Enter...")

        elif sel == '3' or sel == '4':
            type_ = "PickUp" if sel == '3' else "DropOff"
            res_id = get_int("Reservation ID")
            if not res_id: continue
            
            emp_id = get_int("Employee ID")
            loc_id = get_int("Location ID")
            state = get_input("Condition (e.g. Good, Scratched)")
            date_val = get_input("Date (YYYY-MM-DD)")
            
            if all([res_id, emp_id, loc_id]):
                data = {
                    'res_id': res_id, 'emp_id': emp_id, 
                    'loc_id': loc_id, 'state': state, 'date': date_val
                }
                print_result(*model.add_pickup_dropoff(type_, data))
            input("Press Enter...")
        
        elif sel == '5' or sel.lower() == 'q':
            return


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        from model import RentalModel
        m = RentalModel()
        run_admin_interface(m)
    except ImportError:
        print("Error: 'model.py' not found. Please ensure the database model is in the same directory.")
    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: {e}")
        input("Press Enter to Exit...")