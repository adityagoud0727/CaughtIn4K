import sqlite3
from pathlib import Path
from datetime import datetime


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "caughtin4k.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA journal_mode=WAL"
    )

    connection.execute(
        "PRAGMA busy_timeout=10000"
    )

    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def initialize_database():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # --------------------------------------
        # Users
        # --------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # --------------------------------------
        # File Records
        # --------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT,
                original_hash TEXT,
                cleaned_hash TEXT,
                risk_score INTEGER,
                created_at TEXT NOT NULL
            )
        """)

        # --------------------------------------
        # Metadata Findings
        # --------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                category TEXT,
                field_name TEXT,
                field_value TEXT,
                risk_level TEXT,
                FOREIGN KEY (file_id)
                    REFERENCES file_records(id)
            )
        """)

        # --------------------------------------
        # Steganography Operations
        # --------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stego_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                operation TEXT,
                file_hash TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # --------------------------------------
        # Reports
        # --------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                report_type TEXT,
                report_path TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (file_id)
                    REFERENCES file_records(id)
            )
        """)

        # --------------------------------------
        # Audit Logs
        # --------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                filename TEXT,
                status TEXT,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()

    finally:

        connection.close()


# ==========================================
# SAVE FILE ANALYSIS
# ==========================================

def save_analysis(
    filename,
    file_type,
    original_hash,
    risk_score,
    findings
):

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO file_records
            (
                filename,
                file_type,
                original_hash,
                risk_score,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            filename,
            file_type,
            original_hash,
            risk_score,
            now
        ))

        file_id = cursor.lastrowid

        for finding in findings:

            cursor.execute("""
                INSERT INTO metadata_findings
                (
                    file_id,
                    category,
                    field_name,
                    field_value,
                    risk_level
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                file_id,
                finding.get(
                    "category",
                    "Unknown"
                ),
                finding.get(
                    "field",
                    "Unknown"
                ),
                str(
                    finding.get(
                        "value",
                        ""
                    )
                ),
                finding.get(
                    "risk",
                    "LOW"
                )
            ))

        cursor.execute("""
            INSERT INTO audit_logs
            (
                action,
                filename,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            "File Analysis",
            filename,
            "SUCCESS",
            now
        ))

        connection.commit()

        return file_id

    except sqlite3.Error:

        if connection:
            connection.rollback()

        raise

    finally:

        if connection:
            connection.close()


# ==========================================
# GET ANALYSIS HISTORY
# ==========================================

def get_analysis_history():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                filename,
                file_type,
                original_hash,
                cleaned_hash,
                risk_score,
                created_at
            FROM file_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:

        connection.close()


# ==========================================
# GET FILE FINDINGS
# ==========================================

def get_file_findings(file_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                category,
                field_name,
                field_value,
                risk_level
            FROM metadata_findings
            WHERE file_id = ?
            ORDER BY id
        """, (
            file_id,
        ))

        return cursor.fetchall()

    finally:

        connection.close()


# ==========================================
# ADD AUDIT LOG
# ==========================================

def add_audit_log(
    action,
    filename,
    status
):

    connection = get_connection()

    try:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        connection.execute("""
            INSERT INTO audit_logs
            (
                action,
                filename,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            action,
            filename,
            status,
            now
        ))

        connection.commit()

    finally:

        connection.close()


# ==========================================
# SAVE STEGANOGRAPHY OPERATION
# ==========================================

def save_stego_operation(
    filename,
    operation,
    file_hash
):

    connection = get_connection()

    try:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        connection.execute("""
            INSERT INTO stego_operations
            (
                filename,
                operation,
                file_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            filename,
            operation,
            file_hash,
            now
        ))

        connection.commit()

    finally:

        connection.close()


# ==========================================
# TEST DATABASE
# ==========================================

if __name__ == "__main__":

    initialize_database()

    print(
        "CaughtIn4K database initialized successfully."
    )

    print(
        f"Database location: {DB_PATH}"
    )