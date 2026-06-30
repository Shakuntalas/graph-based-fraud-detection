"""SQLite persistence for users, transactions, and alerts."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import bcrypt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "users.db"
_INITIALIZED_PATHS: set[str] = set()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    database_path = Path(DATABASE_PATH)
    database_dir = database_path.parent
    database_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create required SQLite tables if they do not exist."""
    database_path = Path(DATABASE_PATH)
    path_key = str(database_path)
    if path_key in _INITIALIZED_PATHS:
        return

    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                account_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                probability REAL NOT NULL,
                prediction INTEGER NOT NULL,
                anomaly_score REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                account_id TEXT,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
            );
            """
        )
    _INITIALIZED_PATHS.add(path_key)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def generate_account_id() -> str:
    """Generate PaySim-style customer IDs: C100000001, C100000002, ..."""
    with get_connection() as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM users").fetchone()
    return f"C{100000001 + int(row['total'])}"


def create_user(username: str, password: str) -> tuple[bool, str, dict[str, Any] | None]:
    init_db()
    account_id = generate_account_id()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (username, password_hash, account_id, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (username, hash_password(password), account_id, utc_now()),
            )
            user_id = cursor.lastrowid
        return True, "User registered successfully.", get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return False, "Username already exists.", None


def get_user_by_username(username: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    user = get_user_by_username(username)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


def save_transaction(
    user_id: int | None,
    sender: str,
    receiver: str,
    amount: float,
    transaction_type: str,
    probability: float,
    prediction: int,
    anomaly_score: float = 0.0,
) -> dict[str, Any]:
    init_db()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO transactions
                (user_id, sender, receiver, amount, transaction_type, probability, prediction, anomaly_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, sender, receiver, amount, transaction_type, probability, prediction, anomaly_score, utc_now()),
        )
        transaction_id = cursor.lastrowid
    return get_transaction_by_id(transaction_id)


def get_transaction_by_id(transaction_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
    return dict(row)


def list_transactions(limit: int = 200, user_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT t.*, u.username
        FROM transactions t
        LEFT JOIN users u ON t.user_id = u.id
    """
    params: tuple[Any, ...] = ()

    if user_id is not None:
        query += " WHERE t.user_id = ?"
        params = (user_id,)

    query += " ORDER BY t.id DESC LIMIT ?"
    params = (*params, limit)

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def count_transactions_by_sender(sender: str, limit: int = 50) -> int:
    query = """
        SELECT COUNT(*) AS total
        FROM (
            SELECT 1
            FROM transactions
            WHERE sender = ?
            ORDER BY id DESC
            LIMIT ?
        )
    """
    with get_connection() as connection:
        row = connection.execute(query, (sender, limit)).fetchone()
    return int(row["total"]) if row else 0


def create_alert(
    alert_type: str,
    message: str,
    severity: str = "high",
    transaction_id: int | None = None,
    account_id: str | None = None,
) -> None:
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO alerts (transaction_id, account_id, alert_type, message, severity, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (transaction_id, account_id, alert_type, message, severity, utc_now()),
        )


def list_alerts(limit: int = 50) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_user_metrics() -> dict[str, int]:
    with get_connection() as connection:
        total_users = connection.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
        active_users = connection.execute("SELECT COUNT(DISTINCT user_id) AS total FROM transactions WHERE user_id IS NOT NULL").fetchone()["total"]
        flagged_users = connection.execute("SELECT COUNT(DISTINCT user_id) AS total FROM transactions WHERE prediction = 1 AND user_id IS NOT NULL").fetchone()["total"]

    return {
        "total_users": int(total_users),
        "active_users": int(active_users),
        "flagged_users": int(flagged_users),
    }


def get_top_risky_accounts(limit: int = 5) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT sender AS account_id, AVG(probability) AS average_probability, COUNT(*) AS total
            FROM transactions
            GROUP BY sender
            ORDER BY average_probability DESC, total DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
