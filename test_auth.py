from app.security.auth import authenticate_user


username = input("Username: ")
password = input("Password: ")

success, user = authenticate_user(
    username,
    password
)

if success:
    print(f"Login successful. Welcome {user['username']}!")
else:
    print("Invalid username or password.")