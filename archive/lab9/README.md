# Smart Library - Laboratory Work 9

This project implements a data submission system and multi-window navigation using FastAPI and Flet.

## Technical Implementation

### Backend (FastAPI & SQLite3)
* **POST Endpoint:** Added a `/books` route to insert new records into the database.
* **Data Validation:** Used Pydantic models to validate incoming JSON data.
* **Error Handling:** Implemented checks for duplicate IDs using sqlite3.IntegrityError.
* **Persistence:** Data is stored in smartlib_users.db to ensure it remains available after restart.

### Frontend (Flet)
* **Navigation:** Implemented ft.NavigationBar to switch between the book list and the entry form.
* **Data Submission:** Created a form that sends data to the API using the requests library.
* **User Feedback:** Added SnackBar notifications for success and error states.

## How to Run

1. Install dependencies:
   pip install fastapi uvicorn requests flet

2. Start the API (Terminal 1):
   uvicorn lab9_api:app --reload --port 8000

3. Start the UI (Terminal 2):
   python lab9_main_demo.py