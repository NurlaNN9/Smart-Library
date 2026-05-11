# ============================================================
# LABORATORY WORK #9
# "Sending Data via FastAPI + SQLite3 (POST) and
#  Navigation Between Windows"
# ------------------------------------------------------------
# Project: Smart Library
# File:    main.py   (Lab 9 — Flet client with NavigationBar)
#
# Goal of LAB 9 (client side):
#   - Window 1: list of books loaded from FastAPI (GET /books)
#   - Window 2: form that sends a new book to FastAPI (POST /books)
#   - Switch between windows using ft.NavigationBar
#   - Show success / error messages with SnackBar
#
# How to run:
#   1) Start the API in one terminal:
#        uvicorn api:app --reload --port 8000
#   2) Start this Flet app in another terminal:
#        python main.py
# ============================================================

import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"


def main(page: ft.Page):
    page.title = "Smart Library — Lab 9"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # ── Form fields ────────────────────────────────────
    f_id     = ft.TextField(label="ID (number)", width=320)
    f_title  = ft.TextField(label="Title",       width=320)
    f_author = ft.TextField(label="Author",      width=320)
    f_genre  = ft.TextField(label="Genre",       width=320)
    f_tag    = ft.Dropdown(
        label="Type",
        width=320,
        options=[
            ft.dropdown.Option("Physical"),
            ft.dropdown.Option("E-Book"),
        ],
        value="Physical",
    )

    # ── DataTable ──────────────────────────────────────
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Title")),
            ft.DataColumn(ft.Text("Author")),
            ft.DataColumn(ft.Text("Genre")),
            ft.DataColumn(ft.Text("Type")),
        ],
        rows=[],
    )

    # ── Helpers ────────────────────────────────────────
    def show_snack(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def load_table():
        try:
            response = requests.get(f"{API_URL}/books", timeout=5)
            table.rows.clear()
            for item in response.json():
                table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(item["id"]))),
                        ft.DataCell(ft.Text(item["title"])),
                        ft.DataCell(ft.Text(item["author"])),
                        ft.DataCell(ft.Text(item.get("genre") or "")),
                        ft.DataCell(ft.Text(item.get("tag") or "")),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot connect to API", ft.Colors.RED)

    def submit_record(e):
        # Validate fields
        if not (f_id.value and f_title.value and f_author.value
                and f_genre.value and f_tag.value):
            show_snack("Please fill in all fields!", ft.Colors.RED)
            return

        # ID must be a number (matches our books.id column)
        try:
            book_id = int(f_id.value.strip())
        except ValueError:
            show_snack("ID must be a number!", ft.Colors.RED)
            return

        payload = {
            "id":     book_id,
            "title":  f_title.value.strip(),
            "author": f_author.value.strip(),
            "genre":  f_genre.value.strip(),
            "tag":    f_tag.value,
        }

        try:
            response = requests.post(f"{API_URL}/books", json=payload, timeout=5)
            result = response.json()

            if "error" in result:
                # ID already exists in SQLite
                show_snack(f"Error: {result['error']}", ft.Colors.RED)
            else:
                # Clear form fields
                f_id.value = ""
                f_title.value = ""
                f_author.value = ""
                f_genre.value = ""
                f_tag.value = "Physical"

                show_snack("Book added successfully!")
                load_table()                  # refresh from API

                # Switch back to Window 1
                nav.selected_index = 0
                main_view.visible = True
                add_view.visible = False
                page.update()

        except Exception:
            show_snack("API connection error", ft.Colors.RED)

    # ── Navigation ─────────────────────────────────────
    def nav_change(e):
        index = e.control.selected_index
        main_view.visible = (index == 0)
        add_view.visible = (index == 1)
        if index == 0:
            load_table()
        page.update()

    nav = ft.NavigationBar(
        selected_index=0,
        on_change=nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.LIST_ALT,
                label="Books",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_BOX,
                label="Add New",
            ),
        ],
    )

    # ── Window 1: Books list ───────────────────────────
    main_view = ft.Column(
        visible=True,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Smart Library — Books", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("All Books (from API)",
                                    size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Refresh",
                                icon=ft.Icons.REFRESH,
                                on_click=lambda _: load_table(),
                            ),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[table],
                    ),
                ]),
            ),
        ],
    )

    # ── Window 2: Add new book ─────────────────────────
    add_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Add New Book", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
            ),
            ft.Container(
                padding=24,
                content=ft.Column([
                    ft.Text("Fill in all fields", size=16, color="#757575"),
                    ft.Container(height=8),
                    f_id,
                    f_title,
                    f_author,
                    f_genre,
                    f_tag,
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        "Submit Book",
                        icon=ft.Icons.SAVE,
                        bgcolor="#1565c0",
                        color=ft.Colors.WHITE,
                        width=320,
                        on_click=submit_record,
                    ),
                ]),
            ),
        ],
    )

    # ── Layout ─────────────────────────────────────────
    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Stack([main_view, add_view]),
                ),
                nav,
            ],
        )
    )

    load_table()   # load data on startup


ft.app(target=main)
