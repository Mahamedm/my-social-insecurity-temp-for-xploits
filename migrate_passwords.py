from social_insecurity import bcrypt, create_app, sqlite


def migrate_passwords():
    app = create_app()
    with app.app_context():
        #db = sqlite.connection
        #users = db.execute("SELECT id, password FROM Users").fetchall()
        users = sqlite.connection.execute("SELECT id, password FROM Users").fetchall()
        print(users)

        for user in users:
            user_id, password = user["id"], user["password"]
            if not password.startswith("$2b$"):
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

                q = """UPDATE Users SET password = ? WHERE id = ?"""
                # Update the password in the database with the hashed version
                sqlite.query(
                    hashed_password, 
                    user_id
                )

        print("Password migration completed successfully.")

if __name__ == "__main__":
    migrate_passwords()