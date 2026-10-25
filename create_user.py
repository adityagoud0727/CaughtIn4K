from app.database.db import initialize_database
from app.security.auth import create_user


initialize_database()

username = input("Create username: ")
password = input("Create password: ")

success, message = create_user(username, password)

print(message)