import sys
import os
import threading
import time
import json
import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from difflib import get_close_matches

# -----------------------------------------------------------------------------
# LOCAL MODULES
# -----------------------------------------------------------------------------
from model import RentalModel
try:
    from view import RentalView, PseudoConsole
except ImportError:
    pass

import admin

# -----------------------------------------------------------------------------
# MQTT CONFIGURATION
# -----------------------------------------------------------------------------
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

BROKER = "test.mosquitto.org"
TOPIC_REQUEST = "car_rental/payment/request"
TOPIC_RESPONSE = "car_rental/payment/response"


# -----------------------------------------------------------------------------
# BACKGROUND BANK AGENT (MOCKED)
# -----------------------------------------------------------------------------
def run_bank_listener():
    if not MQTT_AVAILABLE: return
    try:
        def on_connect(client, userdata, flags, rc, properties=None): 
            client.subscribe(TOPIC_REQUEST)
            
        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                amount = payload.get('amount')
                
                time.sleep(2) 
                response = {
                    "status": "APPROVED", 
                    "transaction_id": f"VISA-{int(time.time())}", 
                    "amount": amount
                }
                client.publish(TOPIC_RESPONSE, json.dumps(response))
            except: 
                pass 

        bank_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        bank_client.on_connect = on_connect
        bank_client.on_message = on_message
        bank_client.connect(BROKER, 1883, 60)
        bank_client.loop_forever()
    except: 
        pass


# -----------------------------------------------------------------------------
# MAIN CONTROLLER
# -----------------------------------------------------------------------------
class RentalController:
    def __init__(self):
        global MQTT_AVAILABLE 
        
        self.model = RentalModel()
        self.view = RentalView()
        
        # Background bank thread
        self.bank_thread = threading.Thread(target=run_bank_listener, daemon=True)
        self.bank_thread.start()
        
        self.payment_status = None 
        self.payment_timeout_counter = 0

        if MQTT_AVAILABLE:
            self.app_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.app_mqtt.on_message = self.on_bank_response
            try:
                self.app_mqtt.connect(BROKER, 1883, 60)
                self.app_mqtt.subscribe(TOPIC_RESPONSE)
                self.app_mqtt.loop_start()
            except: 
                print("Warning: MQTT Connection Failed. Running in offline mode.")
                MQTT_AVAILABLE = False 

        self._load_init_data()
        self.current_booking = {}
        self.search_results = []
        self.current_cat_id = 1
        
        self.HIERARCHY = {
            1: ["City Car", "Compact Hatch"], 
            2: ["Crossover", "Full SUV"], 
            3: ["Luxury Compact", "Executive"], 
            4: ["MPV", "Passenger Van"]
        }
        self.SUBCAT_MAPPING = {
            "City Car": ["Yaris", "Panda", "Micra", "i10", "Aygo", "Picanto", "500"], 
            "Compact Hatch": ["Clio", "Polo", "Corsa", "i20", "Fiesta", "Astra", "Tipo", "Series 1", "A3", "A-Class"], 
            "Crossover": ["C-HR", "Vitara", "T-Roc", "Duster", "Captur", "Qashqai", "Tucson", "3008"], 
            "Full SUV": ["X5", "Q8", "Tiguan", "S90"], 
            "Luxury Compact": ["A-Class", "Series 1", "A3"], 
            "Executive": ["Octavia", "S90", "Model 3", "C-Class", "Corolla"], 
            "MPV": ["C4 Grand", "Zafira"], 
            "Passenger Van": ["Vito", "Transporter", "Transit"]
        }
        self.INSURANCE_PLANS = [
            {"id": 0, "name": "Basic", "price": 0, "desc": "Standard Liability"}, 
            {"id": 1, "name": "Full", "price": 15, "desc": "Zero Excess"}
        ]
        
        self.show_role_selector()
        self.view.mainloop()

    def on_bank_response(self, client, userdata, msg):
        try: 
            self.payment_status = json.loads(msg.payload.decode())
        except: 
            pass

    def _load_init_data(self):
        try:
            s1, locs = self.model.get_locations()
            s2, cats = self.model.get_categories()
            
            self.loc_map = {r['address']: r['id'] for r in locs} if s1 and locs else {}
            self.locations = list(self.loc_map.keys())
            
            self.cat_map = {r['category_name']: r['id'] for r in cats} if s2 and cats else {}
            self.categories = list(self.cat_map.keys())
        except: 
            pass

    def show_role_selector(self):
        self.view.show_role_selection(
            admin_command=self.launch_admin_terminal, 
            user_command=self.handle_user
        )

    def handle_user(self): 
        self.view.show_main_screen(rent_command=self.goto_customer_details)

    def launch_admin_terminal(self):
        try:
            self.view.withdraw() 
            self.console = PseudoConsole(self.view)
            
            if self.console:
                sys.stdout = self.console
                sys.stdin = self.console
                sys.stderr = self.console
            
            def run_admin_thread():
                try: 
                    admin.run_admin_interface(self.model)
                except Exception as e: 
                    print(f"CRITICAL ERROR INSIDE THREAD: {e}")
                finally: 
                    self.view.after(0, self.view.destroy)

            t = threading.Thread(target=run_admin_thread, daemon=True)
            t.start()
        except Exception as e:
            messagebox.showerror("Crash Report", f"Error launching Admin:\n{str(e)}")
            self.view.deiconify() 

    def show_home(self): 
        self.view.show_main_screen(rent_command=self.goto_customer_details)

    def goto_customer_details(self): 
        self.view.show_customer_screen(submit_command=self.save_customer_and_next)
    
    # -------------------------------------------------------------------------
    # VALIDATION LOGIC
    # -------------------------------------------------------------------------
    def save_customer_and_next(self):
        data = self.view.get_customer_data()
        
        if not all(data.values()): 
            self.view.show_error("All fields are required!")
            return

        if not re.match(r"^\d{10}$", data['phone']): 
            self.view.show_error("Phone must be exactly 10 digits")
            return

        # License must be strictly 9 numbers
        license_pattern = r"^\d{9}$"
        if not re.match(license_pattern, data['license'].replace(" ", "")):
            self.view.show_error("Invalid License ID.\nMust be exactly 9 numbers.")
            return

        # Intelligent Email Validation
        email = data['email'].lower().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.view.show_error("Invalid Email Address format.")
            return

        domain_part = email.split('@')[-1]
        
        major_providers = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
            'icloud.com', 'live.com', 'msn.com', 'aol.com', 'yahoo.gr'
        ]
        
        # Check for close matches (typos) in domain
        matches = get_close_matches(domain_part, major_providers, n=1, cutoff=0.85)
        if matches and domain_part != matches[0]:
            self.view.show_error(f"Invalid email domain: '{domain_part}'.\nDid you mean '{matches[0]}'?")
            return

        if domain_part.endswith((".con", ".cmo", ".hotmai")):
             self.view.show_error(f"It looks like there is a typo in your email extension: '{domain_part}'")
             return

        # Age and License Duration Logic
        try:
            dob = datetime.strptime(data['dob'], "%d/%m/%Y").date()
            issue_date = datetime.strptime(data['issue_date'], "%d/%m/%Y").date()
            today = datetime.now().date()

            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age < 23:
                self.view.show_error(f"Driver must be at least 23 years old.\nCurrent Age: {age}")
                return

            license_years = today.year - issue_date.year - ((today.month, today.day) < (issue_date.month, issue_date.day))
            
            if license_years < 1:
                self.view.show_error(f"License must be held for at least 1 year.\nCurrent duration: {license_years} years")
                return
            
            if issue_date.year < (dob.year + 18):
                 self.view.show_error("License Issue Date is invalid (issued before age 18).")
                 return

        except ValueError:
            self.view.show_error("Invalid Date Format. Please use DD/MM/YYYY")
            return

        self.current_booking['customer'] = data
        self.back_to_reservation()

    # -------------------------------------------------------------------------
    # BOOKING FLOW
    # -------------------------------------------------------------------------

    def back_to_reservation(self):
        slots = [f"{h:02d}:{m:02d}" for h in range(7, 23) for m in (0, 30)]
        self.view.show_reservation_screen(
            search_command=self.perform_search, 
            car_types=self.categories, 
            locations=self.locations, 
            time_slots=slots
        )

    def perform_search(self):
        c = self.view.combos
        cal = self.view.calendar_selection
        
        if not cal['start'] or not cal['end']: 
            self.view.show_error("Please select a date range!")
            return
            
        self.current_booking['dates'] = {
            'start': cal['start'], 'end': cal['end'], 
            'start_time': c['pickup_time'].get(), 'end_time': c['dropoff_time'].get()
        }
        
        cat_id = self.cat_map.get(c['car_type'].get(), 1)
        loc_id = self.loc_map.get(c['pickup_loc'].get(), 1)
        self.current_booking['loc_id'] = loc_id
        
        success, cars = self.model.get_available_cars_for_booking(cat_id, loc_id)
        if not success: cars = []
        
        s_str = cal['start'].strftime("%Y-%m-%d")
        e_str = cal['end'].strftime("%Y-%m-%d")
        
        s2, busy = self.model.get_conflicting_reservations(s_str, e_str)
        busy_ids = {r['car_id'] for r in busy} if s2 and busy else set()
        
        self.search_results = [c for c in cars if c['car_id'] not in busy_ids]
        self.current_cat_id = cat_id
        self.refresh_subcategory_view()

    def refresh_subcategory_view(self):
        vars = self.view.filter_vars
        filtered = self.search_results[:]
        
        if vars.get("automatic_only") and vars["automatic_only"].get(): 
            filtered = [c for c in filtered if c['gearbox'] == 'Automatic']
        if vars.get("diesel_only") and vars["diesel_only"].get(): 
            filtered = [c for c in filtered if c['fuel'] == 'Diesel']
        if vars.get("hybrid_only") and vars["hybrid_only"].get(): 
            filtered = [c for c in filtered if c['fuel'] in ['Hybrid', 'Electric']]
        
        hierarchy = self.HIERARCHY.get(self.current_cat_id, [])
        display_data = {}
        
        for sub in hierarchy:
            models = self.SUBCAT_MAPPING.get(sub, [])
            matches = [c for c in filtered if c['model'] in models or c['brand'] in models]
            best = min(matches, key=lambda x: x['price_per_day']) if matches else None
            
            if best: 
                display_data[sub] = {
                    'available': True, 
                    'min_price': best['price_per_day'], 
                    'car': {
                        'make': best['brand'], 'model': best['model'], 
                        'trans': best['gearbox'], 'fuel': best['fuel'], 
                        'seats': best['seats'], 'bags': best['bags']
                    }
                }
            else: 
                display_data[sub] = {'available': False, 'car': {}, 'min_price': 0}
                
        self.view.show_subcategory_screen(
            subcats_status=display_data, 
            on_subcat_click=self.select_subcategory, 
            on_filter_change=self.refresh_subcategory_view, 
            on_home_click=self.back_to_reservation
        )

    def select_subcategory(self, subcat_name):
        filtered = self.search_results
        models = self.SUBCAT_MAPPING.get(subcat_name, [])
        matches = [c for c in filtered if c['model'] in models or c['brand'] in models]
        
        if not matches: return
        
        target_car = min(matches, key=lambda x: x['price_per_day'])
        self.current_booking['car'] = target_car
        self.current_booking['subcat_name'] = subcat_name
        self.show_summary_screen()

    def show_summary_screen(self):
        car = self.current_booking['car']
        summary = {
            'subcat': self.current_booking['subcat_name'], 
            'price': car['price_per_day'], 
            'trans': car['gearbox'], 
            'fuel': car['fuel'], 
            'seats': car['seats'], 
            'bags': car['bags']
        }
        self.view.show_booking_overview(
            summary=summary, 
            insurance_options=self.INSURANCE_PLANS, 
            late_policy="A €50 Security Deposit is charged upfront...", 
            on_back_click=self.back_to_reservation, 
            on_next_click=self.calculate_invoice, 
            on_home_click=self.show_home
        )

    def calculate_invoice(self):
        d1 = self.current_booking['dates']['start']
        d2 = self.current_booking['dates']['end']
        
        days = (d2 - d1).days
        days = 1 if days < 1 else days
        
        daily_rate = self.current_booking['car']['price_per_day']
        rental_total = days * daily_rate
        
        ins_id = self.view.insurance_var.get()
        ins_plan = next((p for p in self.INSURANCE_PLANS if p['id'] == ins_id), self.INSURANCE_PLANS[0])
        
        grand_total = rental_total + (days * ins_plan['price']) + 50.0
        
        inv_data = {
            'category': self.current_booking['subcat_name'], 
            'days': days, 
            'rental_total': rental_total, 
            'daily_rate': daily_rate, 
            'ins_name': ins_plan['name'], 
            'ins_total': (days * ins_plan['price']), 
            'deposit': 50.0, 
            'grand_total': grand_total
        }
        
        self.view.show_invoice_screen(
            invoice_data=inv_data, 
            on_back_click=self.show_summary_screen, 
            on_checkout_click=lambda: self.view.show_payment_screen(
                amount=grand_total, 
                on_pay_click=lambda: self.initiate_payment(inv_data), 
                on_back_click=self.show_summary_screen
            )
        )

    def initiate_payment(self, inv_data):
        pay_data = self.view.get_payment_data()
        
        cvv = pay_data.get('cvv', '').strip()
        card_num = pay_data.get('card_num', '').replace(" ", "")

        if not cvv.isdigit() or len(cvv) != 3:
            self.view.show_error("Security Code (CVV) must be exactly 3 digits.")
            return

        if not card_num.isdigit() or len(card_num) != 16:
            self.view.show_error("Card number must be 16 digits.")
            return
        
        # Payment Processing UI
        self.view.config(cursor="watch")
        self.view.title("Processing Payment... Please Wait")
        self.view.update() 

        self.payment_status = None
        self.payment_timeout_counter = 0

        # MQTT Logic
        if MQTT_AVAILABLE:
            req = {"amount": inv_data['grand_total'], "card": card_num[-4:]}
            try: 
                self.app_mqtt.publish(TOPIC_REQUEST, json.dumps(req))
            except: 
                self.fake_payment_success(inv_data)
                return
            self.view.after(500, lambda: self.check_payment_status(inv_data))
        else:
            self.view.after(2000, lambda: self.fake_payment_success(inv_data))

    def check_payment_status(self, inv_data):
        if self.payment_status:
            self.reset_ui()
            if self.payment_status.get('status') == 'APPROVED':
                self.finalize_booking(inv_data)
            else: 
                messagebox.showerror("Failed", "Payment Declined by Bank.")
            return

        self.payment_timeout_counter += 1
        if self.payment_timeout_counter > 20: 
            self.reset_ui()
            messagebox.showinfo("Offline Approval", "Bank server slow. Approving locally.")
            self.finalize_booking(inv_data)
            return

        self.view.after(500, lambda: self.check_payment_status(inv_data))

    def reset_ui(self):
        self.view.config(cursor="")
        self.view.title("Car Rental Agency App")

    def fake_payment_success(self, inv_data):
        self.reset_ui()
        self.finalize_booking(inv_data)

    def finalize_booking(self, inv_data):
        try:
            d = self.current_booking
            cust_data = d['customer']
            
            s, existing = self.model.get_customer_by_email(cust_data['email'])
            cust_id = existing['customer_id'] if s and existing else self.model.add_customer(cust_data)[1]
            
            res_data = {
                'p_date': d['dates']['start'].strftime("%Y-%m-%d"), 
                'd_date': d['dates']['end'].strftime("%Y-%m-%d"), 
                'car_id': d['car']['car_id'], 
                'p_loc': d['loc_id'], 
                'd_loc': d['loc_id'], 
                'cust_id': cust_id, 
                'ins_id': self.view.insurance_var.get(), 
                'cat_id': self.cat_map.get(d.get('subcat_name'), 1)
            }
            
            s, res_id = self.model.add_reservation(res_data)
            if s: 
                self.model.add_payment(res_id, inv_data['grand_total'], cust_id)
            
            # Blocking Popup
            self.view.show_info("Success!", f"Booking Confirmed!\nReservation ID: #{res_id}")
            
        except Exception as e:
            self.view.show_error(f"Booking Error: {str(e)}")
            
        finally:
            self.current_booking = {} 
            self.view.after(100, self.show_role_selector)

if __name__ == "__main__":
    app = RentalController()