
import base64
import hashlib
import secrets
from datetime import datetime

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.database.db import get_connection


# Argon2 password hashing engine
password_hasher = PasswordHasher()


def hash_password(password):
    """
    Create a secure Argon2 password hash.

    The Argon2 hash itself contains the parameters and salt,
    so the resulting string can safely be stored in the database.
    """

    return password_hasher.hash(password)


def verify_password(stored_hash, password):
    """
    Verify a password against the stored Argon2 hash.
    """

    try:
        return password_hasher.verify(stored_hash, password)

    except VerifyMismatchError:
        return False

    except Exception:
        return False


def create_user(username, password):
    """
    Create a local CaughtIn4K user.
    """

    username = username.strip()

    if not username or not password:
        return False, "Username and password are required."

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check whether username already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )

        if cursor.fetchone():
            return False, "Username already exists."

        password_hash = hash_password(password)

        # Keep a separate random value for the database schema.
        # It is not used as the Argon2 salt.
        salt = secrets.token_hex(16)

        created_at = datetime.now().isoformat(timespec="seconds")

        cursor.execute(
            """
            INSERT INTO users
            (username, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                salt,
                created_at
            )
        )

        connection.commit()

        return True, "User created successfully."

    except Exception as error:

        connection.rollback()

        return False, f"Database error: {error}"

    finally:
        connection.close()


def authenticate_user(username, password):
    """
    Authenticate a local CaughtIn4K user.
    """

    username = username.strip()

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return False, None

        if verify_password(
            user["password_hash"],
            password
        ):

            return True, {
                "id": user["id"],
                "username": user["username"]
            }

        return False, None

    finally:
        connection.close()
