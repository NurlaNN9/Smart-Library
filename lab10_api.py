# ============================================================
# Smart Library API - Lab 10 (DELETE / PUT / Search)
# Endpoints:
#   GET    /books             -> list (optional ?search=...)
#   GET    /books/{book_id}   -> one book
#   POST   /books             -> insert (Lab 9)
#   PUT    /books/{book_id}   -> update (Lab 10)
#   DELETE /books/{book_id}   -> delete (Lab 10)
#
# How to run:
#   pip install fastapi uvicorn requests pydantic
#   uvicorn lab10_api:app --reload --port 8000
#
# Swagger UI: http://127.0.0.1:8000/docs
# ============================================================

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os

app = FastAPI(title="Smart Library API", version="3.0")

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "smartlib_users.db")


# ── Database helpers ───────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Make sure the books table exists (safety net)."""
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


# ── Pydantic model ─────────────────────────────────────
class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    tag: str          # "Physical" or "E-Book"


# ── Root ───────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Smart Library API is running 🚀"}


# ── GET all books (with optional search) ───────────────
@app.get("/books")
def get_books(search: Optional[str] = None):
    conn = get_connection()
    if search:
        like = f"%{search}%"
        rows = conn.execute(
            """SELECT id, title, author, genre, tag
                 FROM books
                WHERE title  LIKE ?
                   OR author LIKE ?
                   OR genre  LIKE ?
                ORDER BY id DESC""",
            (like, like, like),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, title, author, genre, tag FROM books ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── GET one book ───────────────────────────────────────
@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, title, author, genre, tag FROM books WHERE id = ?",
        (book_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return {"error": f"ID '{book_id}' not found"}
    return dict(row)


# ── POST: add a new book (Lab 9) ───────────────────────
@app.post("/books")
def add_book(book: Book):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO books (id, title, author, genre, tag, cover) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (book.id, book.title, book.author, book.genre, book.tag, ""),
        )
        conn.commit()
        conn.close()
        return {"message": "Book added successfully", "book": book.dict()}
    except sqlite3.IntegrityError:
        return {"error": f"ID '{book.id}' already exists"}


# ── PUT: update an existing book (Lab 10) ──────────────
@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    conn = get_connection()
    cursor = conn.execute(
        """UPDATE books
              SET title=?, author=?, genre=?, tag=?
            WHERE id=?""",
        (book.title, book.author, book.genre, book.tag, book_id),
    )
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return {"error": f"ID '{book_id}' not found"}
    return {"message": "Record updated", "id": book_id}


# ── DELETE: remove a book by id (Lab 10) ───────────────
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_connection()
    cursor = conn.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return {"error": f"ID '{book_id}' not found"}
    return {"message": "Record deleted", "id": book_id}
