import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "olympics.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.executescript(
        """
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS tickets;

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'open',
            owner TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


def seed_db(hash_fn) -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        ("admin", hash_fn("admin123"), "admin"),
    )
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        ("trainee", hash_fn("trainee123"), "user"),
    )
    conn.executemany(
        "INSERT INTO tickets (title, description, priority, status, owner) VALUES (?, ?, ?, ?, ?)",
        [
            ("Robot arm stuck", "Arm #4 stopped mid-cycle on line 2", 3, "open", "trainee"),
            ("Battery low warning", "Fleet unit R-12 reporting low battery", 2, "open", "trainee"),
            ("Sensor calibration drift", "Lidar drifting out of spec on R-07", 4, "in_progress", "admin"),
        ],
    )
    conn.commit()
    conn.close()
