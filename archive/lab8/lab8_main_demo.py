# How to run:
#   1) In one terminal:   uvicorn api:app --reload --port 8000
#   2) In another:        python lab8_main_demo.py
# ============================================================

import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"


def main(page: ft.Page):
    page.title = "Smart Library — LAB 8 (FastAPI GET)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    status = ft.Text("", color=ft.Colors.GREY)

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Title")),
            ft.DataColumn(ft.Text("Author")),
            ft.DataColumn(ft.Text("Genre")),
            ft.DataColumn(ft.Text("Tag")),
        ],
        rows=[],
    )

    def load_books(e=None):
        try:
            r = requests.get(f"{API_URL}/books", timeout=5)
            data = r.json()
            table.rows.clear()
            for b in data:
                table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(b["id"]))),
                    ft.DataCell(ft.Text(b["title"])),
                    ft.DataCell(ft.Text(b["author"])),
                    ft.DataCell(ft.Text(b["genre"])),
                    ft.DataCell(ft.Text(b["tag"])),
                ]))
            status.value = f"Loaded {len(data)} books from API ✅"
            status.color = ft.Colors.GREEN
        except Exception as ex:
            status.value = f"Cannot connect to API: {ex}"
            status.color = ft.Colors.RED
        page.update()

    page.add(
        ft.Row([
            ft.Text("Books from FastAPI", size=22, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Reload", icon=ft.Icons.REFRESH,
                              on_click=load_books),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        status,
        ft.Container(height=8),
        ft.Row([table], scroll=ft.ScrollMode.AUTO),
    )

    load_books()


ft.app(target=main)
