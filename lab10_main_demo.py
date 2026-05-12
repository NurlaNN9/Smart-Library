# ============================================================
# Smart Library UI - Lab 10 (DELETE / PUT / Search)
# - Window 1: Books list with Edit + Delete buttons and live Search
# - Window 2: Add new book (POST from Lab 9)
# - Edit modal dialog -> PUT /books/{id}
# - Delete icon       -> DELETE /books/{id}
# - Search field      -> GET /books?search=...
#
# How to run:
#   1) uvicorn lab10_api:app --reload --port 8000
#   2) python lab10_main_demo.py
# ============================================================

import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"


def main(page: ft.Page):
    page.title = "Smart Library — Lab 10"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # ── Add-form fields ────────────────────────────────
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

    # ── Search field ───────────────────────────────────
    search = ft.TextField(
        label="Search by title / author / genre",
        width=360,
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: load_table(e.control.value),
    )

    # ── DataTable (with Actions column) ────────────────
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Title")),
            ft.DataColumn(ft.Text("Author")),
            ft.DataColumn(ft.Text("Genre")),
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
    )

    # ── SnackBar helper ────────────────────────────────
    def show_snack(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    # ── Edit dialog fields ─────────────────────────────
    dlg_id     = ft.TextField(label="ID",     width=300, read_only=True)
    dlg_title  = ft.TextField(label="Title",  width=300)
    dlg_author = ft.TextField(label="Author", width=300)
    dlg_genre  = ft.TextField(label="Genre",  width=300)
    dlg_tag    = ft.Dropdown(
        label="Type",
        width=300,
        options=[
            ft.dropdown.Option("Physical"),
            ft.dropdown.Option("E-Book"),
        ],
        value="Physical",
    )

    def close_dialog(e):
        edit_dialog.open = False
        page.update()

    def save_edit(e):
        try:
            book_id = int(dlg_id.value)
        except (TypeError, ValueError):
            show_snack("Invalid ID", ft.Colors.RED)
            return

        payload = {
            "id":     book_id,
            "title":  (dlg_title.value or "").strip(),
            "author": (dlg_author.value or "").strip(),
            "genre":  (dlg_genre.value or "").strip(),
            "tag":    dlg_tag.value or "Physical",
        }
        try:
            r = requests.put(
                f"{API_URL}/books/{book_id}",
                json=payload,
                timeout=5,
            )
            result = r.json()
        except Exception:
            show_snack("API connection error", ft.Colors.RED)
            return

        edit_dialog.open = False
        if "error" in result:
            show_snack(result["error"], ft.Colors.RED)
        else:
            show_snack("Record updated!")
            load_table(search.value)
        page.update()

    edit_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Book"),
        content=ft.Column(
            [dlg_id, dlg_title, dlg_author, dlg_genre, dlg_tag],
            tight=True,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.ElevatedButton(
                "Save",
                bgcolor="#1565c0",
                color=ft.Colors.WHITE,
                on_click=save_edit,
            ),
        ],
    )
    # IMPORTANT (common mistake from the lab notes):
    page.dialog = edit_dialog

    def open_edit_dialog(row_data: dict):
        dlg_id.value     = str(row_data["id"])
        dlg_title.value  = row_data.get("title", "")
        dlg_author.value = row_data.get("author", "")
        dlg_genre.value  = row_data.get("genre", "") or ""
        dlg_tag.value    = row_data.get("tag", "Physical") or "Physical"
        edit_dialog.open = True
        page.update()

    # ── Load / refresh table ───────────────────────────
    def load_table(search_text: str = ""):
        try:
            params = {}
            if search_text:
                params["search"] = search_text
            response = requests.get(f"{API_URL}/books", params=params, timeout=5)
            data = response.json()

            table.rows.clear()
            for item in data:
                item_id = item["id"]

                # Closure wrappers (avoid late-binding bug in loops)
                def make_delete(iid):
                    def on_delete(e):
                        try:
                            r = requests.delete(f"{API_URL}/books/{iid}", timeout=5)
                            result = r.json()
                        except Exception:
                            show_snack("API connection error", ft.Colors.RED)
                            return
                        if "error" in result:
                            show_snack(result["error"], ft.Colors.RED)
                        else:
                            show_snack(f"Deleted: {iid}")
                            load_table(search.value)
                    return on_delete

                def make_edit(row_data):
                    def on_edit(e):
                        open_edit_dialog(row_data)
                    return on_edit

                table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(item["id"]))),
                        ft.DataCell(ft.Text(item["title"])),
                        ft.DataCell(ft.Text(item["author"])),
                        ft.DataCell(ft.Text(item.get("genre") or "")),
                        ft.DataCell(ft.Text(item.get("tag") or "")),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT,
                                tooltip="Edit",
                                on_click=make_edit(item),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                tooltip="Delete",
                                icon_color=ft.Colors.RED_400,
                                on_click=make_delete(item_id),
                            ),
                        ])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot connect to API", ft.Colors.RED)

    # ── Add (POST) ─────────────────────────────────────
    def submit_record(e):
        if not (f_id.value and f_title.value and f_author.value
                and f_genre.value and f_tag.value):
            show_snack("Please fill in all fields!", ft.Colors.RED)
            return
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
                show_snack(f"Error: {result['error']}", ft.Colors.RED)
            else:
                f_id.value = ""
                f_title.value = ""
                f_author.value = ""
                f_genre.value = ""
                f_tag.value = "Physical"
                show_snack("Book added successfully!")
                load_table(search.value)
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
            load_table(search.value)
        page.update()

    nav = ft.NavigationBar(
        selected_index=0,
        on_change=nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Books"),
            ft.NavigationBarDestination(icon=ft.Icons.ADD_BOX,  label="Add New"),
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
                                on_click=lambda _: load_table(search.value),
                            ),
                        ],
                    ),
                    ft.Container(height=8),
                    search,
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[table]),
                ]),
            ),
        ],
    )

    # ── Window 2: Add new ──────────────────────────────
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
                    f_id, f_title, f_author, f_genre, f_tag,
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

    load_table()


ft.app(target=main)
