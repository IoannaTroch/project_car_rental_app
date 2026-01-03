
# Car Rental Management System

A desktop application for **fleet, customer, and reservation management**, developed in **Python** using the **MVC (Model–View–Controller)** architecture.

## Project Structure

The project consists of the following main files:

- **`controller.py`**  
  Main entry point of the application. Coordinates the logic and the GUI.  
  **Run this file to start the application.**

- **`view.py`**  
  Handles the Graphical User Interface using **Tkinter**.

- **`model.py`**  
  Manages the SQLite database connection and core business logic.

- **`admin.py`**  
  Contains administrative features and elevated permissions.

- **`car_rental_db_attempt6.db`**  
  SQLite database storing vehicles, customers, and reservations.

## Technical Features & Libraries

- **GUI Framework:** `Tkinter` for windows and UI components
- **Image Processing:** `Pillow (PIL)` for loading and displaying vehicle images
- **Messaging (Optional):** `paho-mqtt` for real-time communication.
- **Concurrency:** `threading` and `queue` to keep the UI responsive
- **Error Handling:** Automatic error logging in `system_errors.log`
- **Smart Search:** `difflib` for typo-tolerant vehicle searches

## Key Features

- **Fleet Browsing**  
  Browse vehicles by category (SUV, Compact, Van, Executive, etc.) with images.

- **Reservation Management**  
  Date-based reservations with availability checks.

- **Admin Panel**  
  Administrative control over the fleet and database.

## Installation & Execution

### 1. Prerequisites
Make sure **Python 3.x** is installed on your system.

Install the required dependency:
```bash
pip install Pillow
```
If real-time messaging is enabled, install the optional dependency:
```bash
pip install paho-mqtt
```
**Important:**
For the application to function correctly, all files and images must be located in the same directory.
```text
/car_rental_project
├── controller.py
├── view.py
├── model.py
├── admin.py
├── car_rental_db_attempt6.db
├── system_errors.log
├── *.png (all car images: suv.png, van.png, etc.)
└── *.jpg (background images: bmw_login.jpg, etc.)
```

## How to Use 

Once the application is running, follow these steps to navigate through the system:

### 1. Login
* **User Access:** Most browsing features are available upon launch.
* **Admin Login:** To access elevated features. 


### 2. Vehicle Search
* **Browse Categories:** Use the side or main panel to filter vehicles by type.


### 3. Making a Reservation
* **Selection:** Click on a vehicle to view details and availability.
* **Booking:** Select your desired start and end dates. The system automatically calculates the cost and checks for scheduling conflicts.
* **Confirmation:** Confirm the booking to update the SQLite database in real-time.

### 4. System Monitoring (Admin)
* **Management:** Admins can monitor all active reservations and manage the fleet and customers.
* **Logging:** System activities and errors are tracked in `system_errors.log` for easy maintenance.

##  License
This project is licensed under the MIT License.