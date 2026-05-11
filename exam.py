import flet as ft
import sqlite3

APP_BAR = "#f9a825"
ACCENT = "#1565c0"
DB_NAME = "busgo_smart_pass.db"

def main(page: ft.Page):
    page.title = "BusGo Smart Pass"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1100
    page.window_height = 700
    page.bgcolor = "#f5f5f5"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS smart_pass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            card_number TEXT NOT NULL,
            route TEXT NOT NULL,
            balance REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()

    def show_snackbar(message, color=ft.Colors.GREEN):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=color
            )
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", color=ACCENT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Full Name", color=ACCENT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Card Number", color=ACCENT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Route", color=ACCENT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Balance", color=ACCENT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", color=ACCENT, weight=ft.FontWeight.BOLD)),
        ],
        rows=[]
    )

    def load_table():
        table.rows.clear()
        cursor.execute("SELECT id, full_name, card_number, route, balance, status FROM smart_pass ORDER BY id DESC")
        records = cursor.fetchall()
        for row in records:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(str(row[1]))),
                        ft.DataCell(ft.Text(str(row[2]))),
                        ft.DataCell(ft.Text(str(row[3]))),
                        ft.DataCell(ft.Text(f"{float(row[4]):.2f} AZN")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(row[5]), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.GREEN if str(row[5]).lower() == "active" else ft.Colors.RED,
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=20
                            )
                        ),
                    ]
                )
            )
        page.update()

    full_name = ft.TextField(label="Full Name", width=350, border_color=ACCENT)
    card_number = ft.TextField(label="Card Number", width=350, border_color=ACCENT)
    route_name = ft.TextField(label="Route", width=350, border_color=ACCENT)
    balance = ft.TextField(label="Balance", width=350, border_color=ACCENT)
    status = ft.Dropdown(
        label="Status",
        width=350,
        border_color=ACCENT,
        options=[
            ft.dropdown.Option("Active"),
            ft.dropdown.Option("Inactive")
        ]
    )

    def clear_fields():
        full_name.value = ""
        card_number.value = ""
        route_name.value = ""
        balance.value = ""
        status.value = None

    def go_main(e=None):
        main_window.visible = True
        add_window.visible = False
        load_table()
        page.update()

    def go_add(e=None):
        main_window.visible = False
        add_window.visible = True
        page.update()

    def save_record(e):
        if not full_name.value or not card_number.value or not route_name.value or not balance.value or not status.value:
            show_snackbar("Please fill in all fields", ft.Colors.RED)
            return

        try:
            balance_value = float(balance.value)
        except:
            show_snackbar("Balance must be a number", ft.Colors.RED)
            return

        cursor.execute(
            "INSERT INTO smart_pass (full_name, card_number, route, balance, status) VALUES (?, ?, ?, ?, ?)",
            (full_name.value, card_number.value, route_name.value, balance_value, status.value)
        )
        conn.commit()
        clear_fields()
        load_table()
        go_main()
        show_snackbar("Record added successfully", ft.Colors.GREEN)

    bottom_sheet = ft.BottomSheet(
        ft.Container(
            padding=20,
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text("Quick Actions", size=20, weight=ft.FontWeight.BOLD, color=ACCENT),
                    ft.Divider(),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ADD, color=ACCENT),
                        title=ft.Text("Add Record"),
                        on_click=lambda e: [page.close(bottom_sheet), go_add()]
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.REFRESH, color=ACCENT),
                        title=ft.Text("Refresh Table"),
                        on_click=lambda e: [page.close(bottom_sheet), load_table(), show_snackbar("Table refreshed")]
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.INFO, color=ACCENT),
                        title=ft.Text("About App"),
                        on_click=lambda e: [page.close(bottom_sheet), show_snackbar("BusGo Smart Pass")]
                    ),
                ]
            )
        )
    )

    main_window = ft.Column(
        visible=True,
        expand=True,
        controls=[
            ft.Container(
                bgcolor=APP_BAR,
                padding=15,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("BusGo Smart Pass", color=ft.Colors.WHITE, size=22, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.MENU,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda e: page.open(bottom_sheet)
                        )
                    ]
                )
            ),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Main Window", size=28, weight=ft.FontWeight.BOLD, color=ACCENT),
                                ft.ElevatedButton(
                                    "Add Record",
                                    icon=ft.Icons.ADD,
                                    bgcolor=ACCENT,
                                    color=ft.Colors.WHITE,
                                    on_click=go_add
                                )
                            ]
                        ),
                        ft.Container(
                            bgcolor=ft.Colors.WHITE,
                            padding=15,
                            border_radius=15,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Passenger Smart Pass Records", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Divider(),
                                    ft.Row(
                                        scroll=ft.ScrollMode.AUTO,
                                        controls=[table]
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        ]
    )

    add_window = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.Container(
                bgcolor=APP_BAR,
                padding=15,
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=go_main
                        ),
                        ft.Text("Add Record", color=ft.Colors.WHITE, size=22, weight=ft.FontWeight.BOLD)
                    ]
                )
            ),
            ft.Container(
                padding=30,
                alignment=ft.alignment.center,
                expand=True,
                content=ft.Container(
                    width=500,
                    bgcolor=ft.Colors.WHITE,
                    padding=25,
                    border_radius=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.DIRECTIONS_BUS, size=60, color=APP_BAR),
                            ft.Text("Add Passenger Record", size=24, weight=ft.FontWeight.BOLD, color=ACCENT),
                            ft.Divider(),
                            full_name,
                            card_number,
                            route_name,
                            balance,
                            status,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.ElevatedButton(
                                        "Save",
                                        icon=ft.Icons.SAVE,
                                        bgcolor=ACCENT,
                                        color=ft.Colors.WHITE,
                                        on_click=save_record
                                    ),
                                    ft.OutlinedButton(
                                        "Cancel",
                                        icon=ft.Icons.CANCEL,
                                        on_click=go_main
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
        ]
    )

    load_table()
    page.add(main_window, add_window)

ft.app(target=main)