        def save(e):
            ok, msg = db_update_user(uid, name_field.value, email_field.value)
            crud_msg_ref.current.value = msg
            crud_msg_ref.current.color = TAG_EBOOK if ok else ft.Colors.RED_300
            crud_msg_ref.current.update()
            reload_users()