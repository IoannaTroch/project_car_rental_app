import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime, date, timedelta
import queue  # <--- REQUIRED FOR ADMIN CONSOLE

try:
    from tkcalendar import Calendar
except ImportError:
    print("Please install tkcalendar: pip install tkcalendar")
    exit()

# --- RESOURCE PATH HELPER ---
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class RentalView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Rental Agency App")
        self.resizable(False, False)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.win_width = int(screen_width / 1.5)
        self.win_height = int(screen_height * 0.85)
        x_pos = (screen_width - self.win_width) // 2
        y_pos = (screen_height - self.win_height) // 2
        self.geometry(f"{self.win_width}x{self.win_height}+{x_pos}+{y_pos}")
        
        self.current_bg = None
        self.entries = {} 
        self.combos = {}
        self.filter_vars = {} 
        self.calendar_selection = {"start": None, "end": None}
        self.card_images = {} 
        self.insurance_var = tk.IntVar(value=0) 
        self.payment_vars = {} 

    def clear_screen(self):
        for widget in self.winfo_children(): widget.destroy()

    def set_background(self, image_filename):
        image_path = get_resource_path(image_filename)
        canvas = tk.Canvas(self, width=self.win_width, height=self.win_height, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        try:
            img_open = Image.open(image_path)
            img_resized = img_open.resize((self.win_width, self.win_height), Image.Resampling.LANCZOS)
            self.current_bg = ImageTk.PhotoImage(img_resized)
            canvas.create_image(0, 0, image=self.current_bg, anchor="nw")
        except: canvas.configure(bg="#cccccc")
        return canvas

    # --- SCREEN: ROLE SELECTION ---
    def show_role_selection(self, admin_command, user_command):
        self.clear_screen()
        canvas = self.set_background("bmw_login.jpg")
        
        canvas.create_text(self.win_width/2, 50, text="RENTAL AGENCY PORTAL", font=("Helvetica", 38, "bold"), fill="black")
        btn_frame = tk.Frame(canvas, bg="#cccccc")
        canvas.create_window(self.win_width/2, self.win_height - 150, window=btn_frame)
        
        tk.Button(btn_frame, text="ADMIN ACCESS", font=("Arial", 14, "bold"), 
                  bg="#333333", fg="white", width=20, pady=10, 
                  cursor="hand2", command=admin_command).pack(side="left", padx=20)
        
        tk.Button(btn_frame, text="USER / RENT A CAR", font=("Arial", 14, "bold"), 
                  bg="#2ecc71", fg="white", width=20, pady=10, 
                  cursor="hand2", command=user_command).pack(side="right", padx=20)

    # --- SCREEN 1 & 2 ---
    def show_main_screen(self, rent_command):
        self.clear_screen(); canvas = self.set_background("bmw_login.jpg")
        canvas.create_text(self.win_width/2, 50, text="CAR RENTAL AGENCY", font=("Helvetica", 38, "bold"), fill="black")
        btn = tk.Button(self, text="Rent now!", font=("Arial", 16), bg="green", fg="white", cursor="hand2", command=rent_command)
        canvas.create_window(self.win_width/2, self.win_height - 100, window=btn)

    def show_customer_screen(self, submit_command):
        self.clear_screen(); self.title("Customer Details"); canvas = self.set_background("blurry_car_bg.jpg")
        form_frame = tk.Frame(canvas, bg="#222222", padx=40, pady=30); canvas.create_window(self.win_width/2, self.win_height/2, window=form_frame, anchor="center")
        tk.Label(form_frame, text="Customer Details", font=("Helvetica", 20, "bold"), bg="#222222", fg="white").pack(pady=(0, 20))
        entry_style = {"font": ("Arial", 11), "bg": "#333333", "fg": "white", "insertbackground": "white", "bd": 0, "highlightthickness": 1, "highlightcolor": "#C1E1C1", "highlightbackground": "#333333"}
        def create_field(key, label):
            tk.Label(form_frame, text=label, bg="#222222", fg="#aaaaaa", font=("Arial", 9)).pack(anchor="w")
            e = tk.Entry(form_frame, **entry_style); e.pack(fill="x", pady=(2, 10), ipady=5); self.entries[key] = e 
        create_field("name", "Full Name")
        create_field("phone", "Phone Number")
        create_field("email", "Email Address")
        create_field("address", "Home Address")
        create_field("license", "Driver's License ID")
        date_frame = tk.Frame(form_frame, bg="#222222"); date_frame.pack(fill="x", pady=5)
        def create_formatted_date(parent, key, label):
            tk.Label(parent, text=label, bg="#222222", fg="#aaaaaa", font=("Arial", 9)).pack(anchor="w")
            entry = tk.Entry(parent, **entry_style)
            entry.pack(fill="x", pady=(2, 10), ipady=5)
            entry.insert(0, "DD/MM/YYYY"); entry.config(fg="#aaaaaa")
            def on_in(e): 
                if entry.get() == "DD/MM/YYYY": entry.delete(0, "end"); entry.config(fg="white")
            def on_out(e): 
                if entry.get() == "": entry.insert(0, "DD/MM/YYYY"); entry.config(fg="#aaaaaa")
            def auto_format(e):
                if e.keysym.lower() in ["backspace", "delete", "left", "right"]: return
                text = entry.get().replace("/", "").replace("-", "")
                text = ''.join(filter(str.isdigit, text))[:8] 
                new_text = text[:2] + ("/" + text[2:4] if len(text)>2 else "") + ("/" + text[4:] if len(text)>4 else "")
                entry.delete(0, "end"); entry.insert(0, new_text)
            entry.bind("<FocusIn>", on_in); entry.bind("<FocusOut>", on_out); entry.bind("<KeyRelease>", auto_format)
            self.entries[key] = entry
        left_f = tk.Frame(date_frame, bg="#222222"); left_f.pack(side="left", fill="x", expand=True, padx=(0, 10))
        create_formatted_date(left_f, "dob", "Date of Birth")
        right_f = tk.Frame(date_frame, bg="#222222"); right_f.pack(side="right", fill="x", expand=True)
        create_formatted_date(right_f, "issue_date", "License Issue Date")
        tk.Button(form_frame, text="Search for a car  ➜", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", bd=0, padx=30, pady=12, cursor="hand2", command=submit_command).pack(pady=(20, 0))
    
    def get_customer_data(self): return {k: v.get().strip() for k, v in self.entries.items()}
    def show_error(self, message): messagebox.showwarning("Error", message)
    def show_info(self, title, message): messagebox.showinfo(title, message)

    # --- SCREEN 3: RESERVATION ---
    def show_reservation_screen(self, search_command, car_types, locations, time_slots):
        self.clear_screen(); self.title("Reservation Details"); canvas = self.set_background("blurry_car_bg.jpg")
        main_frame = tk.Frame(canvas, bg="#222222", padx=20, pady=20); canvas.create_window(self.win_width/2, self.win_height/2, window=main_frame, anchor="center")
        tk.Label(main_frame, text="Select Your Itinerary", font=("Helvetica", 18, "bold"), bg="#222222", fg="white").pack(pady=(0, 20))
        input_frame = tk.Frame(main_frame, bg="#222222"); input_frame.pack(fill="x", pady=(0, 10))
        self.option_add('*TCombobox*Listbox.background', '#2b2b2b'); self.option_add('*TCombobox*Listbox.foreground', 'white'); self.option_add('*TCombobox*Listbox.selectBackground', '#C1E1C1'); self.option_add('*TCombobox*Listbox.selectForeground', 'black')
        style = ttk.Style(); style.theme_use('clam'); style.configure("Details.TCombobox", fieldbackground="#2b2b2b", background="#444444", foreground="white", arrowcolor="white", borderwidth=0); style.map('Details.TCombobox', fieldbackground=[('readonly', '#C1E1C1')], foreground=[('readonly', 'black')])
        def create_combo(key, label, vals, r, c, w=25):
            tk.Label(input_frame, text=label, bg="#222222", fg="#aaaaaa", font=("Arial", 9)).grid(row=r, column=c, sticky="w", padx=5)
            cb = ttk.Combobox(input_frame, values=vals, style="Details.TCombobox", font=("Arial", 10), state="readonly", width=w); cb.grid(row=r+1, column=c, padx=5, pady=(0, 10), sticky="ew"); cb.current(0) if vals else None
            self.combos[key] = cb
        create_combo("car_type", "Choose Category", car_types, 0, 0, 30); create_combo("pickup_loc", "Pick-up Location", locations, 2, 0, 58); create_combo("dropoff_loc", "Drop-off Location", locations, 2, 1, 58); create_combo("pickup_time", "Pick-up Time", time_slots, 4, 0, 15); create_combo("dropoff_time", "Drop-off Time", time_slots, 4, 1, 15)
        cal_frame = tk.Frame(main_frame, bg="#222222"); cal_frame.pack(pady=10)
        today = date.today()
        cal = Calendar(cal_frame, selectmode='day', mindate=today, background="#222222", disabledbackground="#222222", bordercolor="#222222", headersbackground="#333333", normalbackground="#444444", foreground='white', normalforeground='white', headersforeground='white'); cal.pack(pady=5)
        cal.tag_config('highlight_edge', background='#006400', foreground='white'); cal.tag_config('highlight_range', background='#90EE90', foreground='black') 
        def on_date(event):
            try: clicked = cal.selection_get()
            except: return
            sel = self.calendar_selection
            if sel["start"] and sel["end"]:
                cal.calevent_remove(); sel["start"] = clicked; sel["end"] = None; cal.calevent_create(clicked, 'Start', 'highlight_edge'); return 
            if sel["start"] is None: sel["start"] = clicked; cal.calevent_create(clicked, 'Start', 'highlight_edge')
            elif sel["end"] is None:
                if clicked < sel["start"]: cal.calevent_remove(); sel["start"] = clicked; cal.calevent_create(clicked, 'Start', 'highlight_edge')
                elif clicked > sel["start"]: sel["end"] = clicked; cal.calevent_create(clicked, 'End', 'highlight_edge'); delta = sel["end"] - sel["start"]
                for i in range(1, delta.days): cal.calevent_create(sel["start"] + timedelta(days=i), 'Range', 'highlight_range')
        cal.bind("<<CalendarSelected>>", on_date)
        tk.Button(main_frame, text="Find Vehicles", font=("Arial", 14, "bold"), bg="#218838", fg="white", bd=0, padx=40, pady=10, cursor="hand2", command=search_command).pack(pady=20)

    # --- SCREEN 4: SUBCATEGORY SELECTION ---
    def show_subcategory_screen(self, subcats_status, on_subcat_click, on_filter_change, on_home_click):
        self.clear_screen(); self.title("Select Class"); canvas = self.set_background("blurry_car_bg.jpg")
        filter_frame = tk.Frame(canvas, bg="#333333", pady=10); canvas.create_window(self.win_width/2, 40, window=filter_frame, width=self.win_width, anchor="center")
        tk.Button(filter_frame, text="⟲ New Search", font=("Arial", 9, "bold"), bg="#555555", fg="white", bd=0, command=on_home_click).pack(side="right", padx=20)
        tk.Label(filter_frame, text="Filters:", font=("Arial", 10, "bold"), bg="#333333", fg="white").pack(side="left", padx=20)
        if "automatic_only" not in self.filter_vars: self.filter_vars["automatic_only"] = tk.IntVar()
        if "diesel_only" not in self.filter_vars: self.filter_vars["diesel_only"] = tk.IntVar()
        if "hybrid_only" not in self.filter_vars: self.filter_vars["hybrid_only"] = tk.IntVar()
        cb_style = {"bg": "#333333", "fg": "white", "selectcolor": "#222222", "activebackground": "#333333", "font": ("Arial", 10)}
        tk.Checkbutton(filter_frame, text="Automatic Only", variable=self.filter_vars["automatic_only"], command=on_filter_change, **cb_style).pack(side="left", padx=10)
        tk.Checkbutton(filter_frame, text="Diesel Only", variable=self.filter_vars["diesel_only"], command=on_filter_change, **cb_style).pack(side="left", padx=10)
        tk.Checkbutton(filter_frame, text="Eco (Hybrid/EV)", variable=self.filter_vars["hybrid_only"], command=on_filter_change, **cb_style).pack(side="left", padx=10)
        cards_container = tk.Frame(canvas, bg="#222222"); canvas.create_window(self.win_width/2, self.win_height/2 + 20, window=cards_container, anchor="center")
        for sub_name, status_info in subcats_status.items():
            self._create_subcategory_card(cards_container, sub_name, status_info['car'], status_info['available'], status_info.get('min_price', 0), on_subcat_click)

    def _create_subcategory_card(self, parent, sub_name, car, is_available, min_price, callback):
        bg_color = "#333333" if is_available else "#222222"
        inner_bg = "#444444" if is_available else "#2b2b2b"
        text_color = "white" if is_available else "#555555"
        card = tk.Frame(parent, bg=bg_color, bd=0, padx=2, pady=2); card.pack(side="left", padx=20, pady=20)
        inner = tk.Frame(card, bg=inner_bg, width=250, height=390); inner.pack(); inner.pack_propagate(False)
        file_map = {"City Car": "city_car.png", "Compact Hatch": "compact.png", "Crossover": "crossover.png", "Full SUV": "suv.png", "Luxury Compact": "luxury_compact.png", "Executive": "executive.png", "MPV": "mpv.png", "Passenger Van": "van.png"}
        filename = file_map.get(sub_name, "default.png")
        try:
            if filename not in self.card_images:
                # Use helper here too
                img = Image.open(get_resource_path(filename)).resize((220, 140), Image.Resampling.LANCZOS)
                self.card_images[filename] = ImageTk.PhotoImage(img)
            img_label = tk.Label(inner, image=self.card_images[filename], bg=inner_bg)
        except: img_label = tk.Label(inner, text="🚗", font=("Arial", 50), bg=inner_bg, fg="#aaaaaa")
        img_label.pack(pady=(30, 10))
        tk.Label(inner, text=sub_name, font=("Helvetica", 16, "bold"), bg=inner_bg, fg=text_color).pack()
        if is_available:
            tk.Label(inner, text=f"From €{min_price:.0f} / day", font=("Arial", 12, "bold"), bg=inner_bg, fg="#2ecc71").pack(pady=(0, 5))
            ex_text = f"e.g. {car['make']} {car['model']}"
        else: ex_text = "Unavailable"
        tk.Label(inner, text=ex_text, font=("Arial", 10, "italic"), bg=inner_bg, fg="#cccccc" if is_available else "#444444").pack(pady=(0, 10))
        if is_available:
            specs = tk.Frame(inner, bg=inner_bg); specs.pack(pady=5)
            def spec(txt): tk.Label(specs, text=txt, font=("Arial", 9), bg=inner_bg, fg="white", padx=5).pack(side="left")
            spec(f"⚙️ {car['trans']}"); spec(f"⛽ {car['fuel']}"); spec(f"👤 x{car['seats']}"); spec(f"🧳 x{car['bags']}")
            btn_fake = tk.Label(inner, text="Select Class", font=("Arial", 11, "bold"), bg="#2ecc71", fg="white", padx=20, pady=8); btn_fake.pack(side="bottom", pady=20)
            def on_click(e): callback(sub_name)
            for w in [card, inner, img_label, btn_fake]: w.bind("<Button-1>", on_click); w.config(cursor="hand2")
        else: tk.Label(inner, text="No cars match filters", font=("Arial", 10), bg=inner_bg, fg="#555555").pack(pady=20)

    # --- SCREEN 5: BOOKING OVERVIEW ---
    def show_booking_overview(self, summary, insurance_options, late_policy, on_back_click, on_next_click, on_home_click):
        self.clear_screen(); self.title("Booking Summary"); canvas = self.set_background("blurry_car_bg.jpg")
        header = tk.Frame(canvas, bg="#222222"); canvas.create_window(self.win_width/2, 40, window=header, width=self.win_width, anchor="center")
        tk.Button(header, text="< Back", font=("Arial", 10, "bold"), bg="#444444", fg="white", bd=0, command=on_back_click).pack(side="left", padx=20)
        tk.Button(header, text="⟲ New Search", font=("Arial", 10, "bold"), bg="#555555", fg="white", bd=0, command=on_home_click).pack(side="right", padx=20)
        tk.Label(header, text="Review Selection", font=("Helvetica", 18, "bold"), bg="#222222", fg="white").pack(side="left", padx=10)
        container = tk.Frame(canvas, bg="#222222", pady=10, padx=20); canvas.create_window(self.win_width/2, self.win_height/2 + 20, window=container, anchor="center")
        card = tk.Frame(container, bg="#333333", width=500); card.pack()
        tk.Label(card, text=f"{summary['subcat']} Class", font=("Helvetica", 20, "bold"), bg="#333333", fg="white").pack(pady=(15, 5))
        file_map = {"City Car": "city_car.png", "Compact Hatch": "compact.png", "Crossover": "crossover.png", "Full SUV": "suv.png", "Luxury Compact": "luxury_compact.png", "Executive": "executive.png", "MPV": "mpv.png", "Passenger Van": "van.png"}
        fname = file_map.get(summary['subcat'], "default.png")
        try:
            if fname not in self.card_images:
                img = Image.open(get_resource_path(fname)).resize((180, 110), Image.Resampling.LANCZOS)
                self.card_images[fname] = ImageTk.PhotoImage(img)
            tk.Label(card, image=self.card_images[fname], bg="#333333").pack(pady=5)
        except: tk.Label(card, text="🚗", font=("Arial", 60), bg="#333333", fg="white").pack(pady=5)
        specs_frame = tk.Frame(card, bg="#333333"); specs_frame.pack(pady=5)
        def spec(txt): tk.Label(specs_frame, text=txt, font=("Arial", 11), bg="#333333", fg="white", padx=10).pack(side="left")
        spec(f"⚙️ {summary['trans']}"); spec(f"⛽ {summary['fuel']}"); spec(f"👤 x{summary['seats']}"); spec(f"🧳 x{summary['bags']}")
        ins_frame = tk.Frame(card, bg="#2b2b2b", padx=10, pady=10); ins_frame.pack(fill="x", pady=10, padx=20)
        tk.Label(ins_frame, text="Choose Insurance:", font=("Arial", 10, "bold"), bg="#2b2b2b", fg="white").pack(anchor="w")
        style = ttk.Style(); style.configure("TRadiobutton", background="#2b2b2b", foreground="white", font=("Arial", 10))
        for plan in insurance_options:
            r = ttk.Radiobutton(ins_frame, text=f"{plan['name']} (+€{plan['price']}/day)", variable=self.insurance_var, value=plan['id'], style="TRadiobutton")
            r.pack(anchor="w", pady=2)
            tk.Label(ins_frame, text=f"   {plan['desc']}", font=("Arial", 8), bg="#2b2b2b", fg="#aaaaaa").pack(anchor="w", pady=(0, 5))
        tk.Label(card, text=late_policy, font=("Arial", 8, "bold"), bg="#333333", fg="#ff6b6b", wraplength=450, justify="center").pack(pady=(0, 10))
        bottom_frame = tk.Frame(card, bg="#333333", pady=15); bottom_frame.pack(side="bottom", fill="x")
        tk.Label(bottom_frame, text=f"€{summary['price']}", font=("Helvetica", 22, "bold"), bg="#333333", fg="#2ecc71").pack(side="left", padx=30)
        tk.Label(bottom_frame, text="/ day", font=("Arial", 10), bg="#333333", fg="#aaaaaa").pack(side="left")
        tk.Button(bottom_frame, text="Next Step ➜", bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), bd=0, padx=25, pady=10, cursor="hand2", command=on_next_click).pack(side="right", padx=30)

    # --- SCREEN 6: FINAL INVOICE ---
    def show_invoice_screen(self, invoice_data, on_back_click, on_checkout_click):
        self.clear_screen(); self.title("Final Invoice"); canvas = self.set_background("blurry_car_bg.jpg")
        outer = tk.Frame(canvas, bg="#222222", padx=2, pady=2); canvas.create_window(self.win_width/2, self.win_height/2, window=outer, anchor="center")
        invoice = tk.Frame(outer, bg="black", padx=30, pady=30, width=500); invoice.pack()
        tk.Label(invoice, text="INVOICE", font=("Helvetica", 24, "bold"), bg="black", fg="white").pack(anchor="w")
        tk.Label(invoice, text=f"Date: {datetime.now().strftime('%d/%m/%Y')}", font=("Arial", 10), bg="black", fg="#aaaaaa").pack(anchor="w", pady=(0, 20))
        car_row = tk.Frame(invoice, bg="#111111", pady=10, padx=10); car_row.pack(fill="x", pady=10)
        tk.Label(car_row, text="🚙", font=("Arial", 20), bg="#111111", fg="white").pack(side="left", padx=10)
        tk.Label(car_row, text=f"{invoice_data['category']} Class", font=("Helvetica", 12, "bold"), bg="#111111", fg="white").pack(side="left")
        tk.Label(car_row, text=f"{invoice_data['days']} Days", font=("Arial", 12, "bold"), bg="#111111", fg="#2ecc71").pack(side="right", padx=10)
        def line_item(txt, price, is_bold=False):
            row = tk.Frame(invoice, bg="black"); row.pack(fill="x", pady=2)
            font = ("Arial", 11, "bold") if is_bold else ("Arial", 11); color = "white" if is_bold else "#cccccc"
            tk.Label(row, text=txt, font=font, bg="black", fg=color).pack(side="left")
            tk.Label(row, text=f"€{price:.2f}", font=font, bg="black", fg=color).pack(side="right")
        tk.Frame(invoice, bg="#444444", height=1).pack(fill="x", pady=10)
        line_item("Rental Rate", invoice_data['rental_total']); tk.Label(invoice, text=f"   ({invoice_data['days']} days x €{invoice_data['daily_rate']})", font=("Arial", 9), bg="black", fg="#666666").pack(anchor="w")
        line_item(f"Insurance ({invoice_data['ins_name']})", invoice_data['ins_total'])
        line_item("Security Deposit (Refundable)", invoice_data['deposit']); tk.Label(invoice, text="   *Returned upon on-time drop-off", font=("Arial", 9), bg="black", fg="orange").pack(anchor="w")
        tk.Frame(invoice, bg="#444444", height=1).pack(fill="x", pady=15)
        total_row = tk.Frame(invoice, bg="black"); total_row.pack(fill="x")
        tk.Label(total_row, text="TOTAL TO PAY", font=("Helvetica", 14, "bold"), bg="black", fg="white").pack(side="left")
        tk.Label(total_row, text=f"€{invoice_data['grand_total']:.2f}", font=("Helvetica", 18, "bold"), bg="black", fg="#2ecc71").pack(side="right")
        btn_frame = tk.Frame(invoice, bg="black"); btn_frame.pack(fill="x", pady=(30, 0))
        tk.Button(btn_frame, text="< Back", font=("Arial", 10), bg="#333333", fg="white", bd=0, padx=15, pady=8, cursor="hand2", command=on_back_click).pack(side="left")
        
        tk.Button(btn_frame, text="Proceed to Checkout ➜", font=("Arial", 11, "bold"), bg="#2ecc71", fg="white", bd=0, padx=20, pady=8, cursor="hand2", command=on_checkout_click).pack(side="right")

    # --- SCREEN 7: SECURE PAYMENT ---
    def show_payment_screen(self, amount, on_pay_click, on_back_click):
        self.clear_screen(); self.title("Secure Checkout"); canvas = self.set_background("blurry_car_bg.jpg")
        
        outer = tk.Frame(canvas, bg="#222222", padx=2, pady=2)
        canvas.create_window(self.win_width/2, self.win_height/2, window=outer, anchor="center")
        
        main_frame = tk.Frame(outer, bg="#222222", padx=30, pady=30, width=500)
        main_frame.pack()

        tk.Label(main_frame, text="SECURE CHECKOUT", font=("Helvetica", 20, "bold"), bg="#222222", fg="white").pack(pady=(0, 5))
        tk.Label(main_frame, text="🔒 256-bit Encrypted Connection", font=("Arial", 10), bg="#222222", fg="#2ecc71").pack(pady=(0, 20))
        tk.Label(main_frame, text=f"Total to Pay: €{amount:.2f}", font=("Arial", 18, "bold"), bg="#222222", fg="white").pack(pady=10)

        form_frame = tk.Frame(main_frame, bg="#222222", pady=10); form_frame.pack(fill="x")
        entry_style = {"font": ("Arial", 11), "bg": "#333333", "fg": "white", "insertbackground": "white", "bd": 0, "highlightthickness": 1, "highlightcolor": "#C1E1C1", "highlightbackground": "#333333"}
        self.payment_vars = {} 

        def create_pay_field(key, label, width=30):
            tk.Label(form_frame, text=label, bg="#222222", fg="#aaaaaa", font=("Arial", 9)).pack(anchor="w")
            var = tk.StringVar(); self.payment_vars[key] = var
            e = tk.Entry(form_frame, textvariable=var, width=width, **entry_style)
            e.pack(fill="x", pady=(2, 10), ipady=5); return e

        tk.Label(form_frame, text="Card Number", bg="#222222", fg="#aaaaaa", font=("Arial", 9)).pack(anchor="w")
        card_var = tk.StringVar(); self.payment_vars["card_num"] = card_var
        c_entry = tk.Entry(form_frame, textvariable=card_var, width=30, **entry_style)
        c_entry.pack(fill="x", pady=(2, 10), ipady=5)

        def format_card_num(event):
            if event.keysym.lower() in ["backspace", "delete", "left", "right"]: return
            text = c_entry.get().replace(" ", "")
            text = ''.join(filter(str.isdigit, text))
            if len(text) > 16: text = text[:16] # Limit 16
            new_text = ""
            for i in range(len(text)):
                if i > 0 and i % 4 == 0: new_text += " "
                new_text += text[i]
            if c_entry.get() != new_text:
                c_entry.delete(0, "end"); c_entry.insert(0, new_text)

        c_entry.bind("<KeyRelease>", format_card_num)

        create_pay_field("holder", "Cardholder Name")

        row = tk.Frame(form_frame, bg="#222222"); row.pack(fill="x")
        ex_frame = tk.Frame(row, bg="#222222"); ex_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(ex_frame, text="Expiry (MM/YY)", bg="#222222", fg="#aaaaaa", font=("Arial", 9)).pack(anchor="w")
        ex_var = tk.StringVar(); self.payment_vars["expiry"] = ex_var
        ex_entry = tk.Entry(ex_frame, textvariable=ex_var, **entry_style)
        ex_entry.pack(fill="x", pady=(2, 10), ipady=5)
        
        ex_entry.insert(0, "MM/YY"); ex_entry.config(fg="#aaaaaa")
        def on_ex_in(e): 
            if ex_entry.get() == "MM/YY": ex_entry.delete(0, "end"); ex_entry.config(fg="white")
        def on_ex_out(e): 
            if ex_entry.get() == "": ex_entry.insert(0, "MM/YY"); ex_entry.config(fg="#aaaaaa")
        def format_expiry(event):
            if event.keysym.lower() in ["backspace", "delete", "left", "right"]: return
            text = ''.join(filter(str.isdigit, ex_entry.get().replace("/", "")))[:4]
            if len(text) >= 2: text = text[:2] + "/" + text[2:]
            ex_entry.delete(0, "end"); ex_entry.insert(0, text)
        ex_entry.bind("<FocusIn>", on_ex_in); ex_entry.bind("<FocusOut>", on_ex_out); ex_entry.bind("<KeyRelease>", format_expiry)

        cv_frame = tk.Frame(row, bg="#222222"); cv_frame.pack(side="right", fill="x", expand=True)
        tk.Label(cv_frame, text="CVV", bg="#222222", fg="#aaaaaa", font=("Arial", 9)).pack(anchor="w")
        
        # --- NEW CODE: CVV INPUT LIMITER (ONLY 3 DIGITS) ---
        cv_var = tk.StringVar(); self.payment_vars["cvv"] = cv_var
        
        def limit_cvv(*args):
            val = cv_var.get()
            clean = ''.join(filter(str.isdigit, val))
            if len(clean) > 3: clean = clean[:3]
            if val != clean: cv_var.set(clean)
            
        cv_var.trace_add("write", limit_cvv)
        # ---------------------------------------------------
        
        tk.Entry(cv_frame, textvariable=cv_var, show="*", **entry_style).pack(fill="x", pady=(2, 10), ipady=5)

        btn_frame = tk.Frame(main_frame, bg="#222222"); btn_frame.pack(fill="x", pady=(20, 0))
        tk.Button(btn_frame, text="Cancel", font=("Arial", 10), bg="#333333", fg="white", bd=0, padx=15, pady=10, cursor="hand2", command=on_back_click).pack(side="left")
        tk.Button(btn_frame, text="CONFIRM PAYMENT", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", bd=0, padx=30, pady=10, cursor="hand2", command=on_pay_click).pack(side="right")

    def get_payment_data(self): return {k: v.get() for k, v in self.payment_vars.items()}

# --- SAFEST PSEUDO-CONSOLE (THREAD-SAFE VERSION) ---
class PseudoConsole(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("ADMIN TERMINAL")
        self.geometry("900x650")
        self.configure(bg="#0c0c0c") 
        self.resizable(False, False)
        
        self.text_area = scrolledtext.ScrolledText(self, state='disabled', bg="black", fg="#00ff00", font=("Consolas", 12), insertbackground="white", bd=0)
        self.text_area.pack(expand=True, fill='both', padx=15, pady=(15, 5))
        
        input_frame = tk.Frame(self, bg="#0c0c0c"); input_frame.pack(fill='x', padx=15, pady=15)
        tk.Label(input_frame, text=">>>", bg="#0c0c0c", fg="#00ff00", font=("Consolas", 14, "bold")).pack(side="left")
        
        self.input_var = tk.StringVar()
        self.input_field = tk.Entry(input_frame, textvariable=self.input_var, bg="#222222", fg="white", font=("Consolas", 12), insertbackground="white", bd=0)
        self.input_field.pack(side="left", fill='x', expand=True, ipady=5)
        self.input_field.bind("<Return>", self.submit_input); self.input_field.focus_set()
        
        self.input_queue = queue.Queue() # Using the imported queue
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.is_active = True

    # FIX: Thread Safety (Using after)
    def write(self, text):
        self.after(0, self._safe_append, text)

    def _safe_append(self, text):
        if not self.is_active: return
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

    def flush(self): pass

    def readline(self):
        if not self.is_active: return ""
        try: return self.input_queue.get()
        except: return ""

    def submit_input(self, event):
        text = self.input_var.get(); self.input_var.set("")
        self.write(f">>> {text}\n")
        self.input_queue.put(text + "\n") # Fix EOF Error

    def on_close(self):
        self.is_active = False
        self.input_queue.put("\n") 
        self.destroy()