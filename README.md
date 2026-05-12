# Smart Library — Laboratory Work 10

This lab extends Lab 9 with full CRUD: deleting and editing records via FastAPI
(`DELETE` / `PUT`) plus server-side search using GET query parameters.

## Technical Implementation

### Backend (FastAPI + SQLite3) — `lab10_api.py`
- **PUT `/books/{book_id}`** — replaces title, author, genre and tag for the
  given id. Returns `{"error": "..."}` if the id does not exist.
- **DELETE `/books/{book_id}`** — removes the row by id; same error contract.
- **GET `/books?search=...`** — optional query parameter; when provided,
  filters rows where `title`, `author` or `genre` match `LIKE %search%`.
- **Validation** — Pydantic `Book` model on every write endpoint.
- **Persistence** — same `smartlib_users.db` SQLite file as Labs 8 / 9.

### Frontend (Flet) — `lab10_main_demo.py`
- **Actions column** with Edit and Delete icon buttons on every row.
- **Closure wrappers** `make_edit` / `make_delete` so each button captures its
  own row id (avoids the classic late-binding bug in loops).
- **Edit modal** (`ft.AlertDialog`) opens with pre-filled fields and sends
  `PUT /books/{id}` on Save. `page.dialog = edit_dialog` is registered so the
  modal actually renders.
- **Live search** — TextField with `on_change` calls `GET /books?search=...`
  for server-side filtering.
- **SnackBar feedback** — green for success, red for errors / connection
  failures.

## Full CRUD flow

```
Flet form  ── POST   /books          ──▶ FastAPI ──▶ SQLite
Flet table ◀── GET   /books[?search] ──  FastAPI ◀── SQLite
Edit dlg   ── PUT    /books/{id}     ──▶ FastAPI ──▶ SQLite
Delete btn ── DELETE /books/{id}     ──▶ FastAPI ──▶ SQLite
```

## How to run

1. Install dependencies:
   ```
   pip install fastapi uvicorn requests flet pydantic
   ```
2. Start the API (Terminal 1):
   ```
   uvicorn lab10_api:app --reload --port 8000
   ```
3. Start the UI (Terminal 2):
   ```
   python lab10_main_demo.py
   ```
4. Optional: open Swagger UI at <http://127.0.0.1:8000/docs> to test
   `PUT` and `DELETE` directly.

## Testing checklist
- [x] Add 2–3 books via the **Add New** tab
- [x] Click the **Delete** icon — row disappears, green snackbar shows
- [x] Click the **Edit** icon — dialog opens pre-filled, Save updates the row
- [x] Type in the **Search** field — table filters in real time
- [x] Try deleting a non-existent ID via Swagger → JSON `error` response
- [x] Restart the app — remaining records persist in SQLite
