#   pip install fastapi uvicorn requests
#   uvicorn api:app --reload --port 8000

from fastapi import FastAPI, HTTPException
import sqlite3
import os

app = FastAPI(title="Smart Library API", version="1.0")

# Use the SAME database file your main.py already uses
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "smartlib_users.db")


# ── Database helper ────────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row     # access columns by name
    return conn


# ── Root endpoint (sanity check) ───────────────────────
@app.get("/")
def root():
    return {"message": "Smart Library API is running 🚀"}


# ── GET all books ──────────────────────────────────────
@app.get("/books")
def get_books():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, author, genre, tag, cover FROM books ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ── GET one book by id ─────────────────────────────────
@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, title, author, genre, tag, cover FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return dict(row)


# ── GET all users (without password hash) ──────────────
@app.get("/users")
def get_users():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, email, role FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
