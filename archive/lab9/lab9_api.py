# Smart Library API - Lab 9 (POST & SQLite Integration)
# - Endpoint: GET /books (list) & POST /books (insert)
# - Validation: Pydantic models

# ===========================
# How to run:
#   pip install fastapi uvicorn requests
#   uvicorn api:app --reload --port 8000
#
# Test in browser:
#   http://127.0.0.1:8000/docs        -> Swagger UI (try POST here)
#   http://127.0.0.1:8000/books       -> JSON list of books
# ============================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI(title="Smart Library API", version="2.0")

# Same database file used by smartlibrary-2.py
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "smartlib_users.db")


# ── Database helpers ───────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Make sure the books table exists (safety net for Lab 9)."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id     INTEGER PRIMARY KEY,
            title  TEXT NOT NULL,
            author TEXT NOT NULL,
            genre  TEXT,
            tag    TEXT,
            cover  TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ── Pydantic model (input validation) ──────────────────
class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    tag: str          # "Physical" or "E-Book"


# ── Root endpoint ──────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Smart Library API is running 🚀"}


# ── GET all books ──────────────────────────────────────
@app.get("/books")
def get_books():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, author, genre, tag FROM books ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── GET one book by id ─────────────────────────────────
@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, title, author, genre, tag FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return dict(row)


# ── POST: add a new book ───────────────────────────────
@app.post("/books")
def add_book(book: Book):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO books (id, title, author, genre, tag, cover) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (book.id, book.title, book.author, book.genre, book.tag, "")
        )
        conn.commit()
        conn.close()
        return {"message": "Book added successfully", "book": book}
    except sqlite3.IntegrityError:
        return {"error": f"ID '{book.id}' already exists"}
