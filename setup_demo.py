import sqlite3
import os
from pathlib import Path

def create_demo_db():
    db_path = Path("data/demo.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Creating demo database at {db_path}...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        total_amount DECIMAL(10,2),
        status VARCHAR(20),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS legacy_metrics (
        metric_id INTEGER PRIMARY KEY,
        val_x FLOAT,
        flag_y INTEGER
    )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO users (id, email, is_active) VALUES (1, 'alice@example.com', 1)")
    cursor.execute("INSERT OR IGNORE INTO users (id, email, is_active) VALUES (2, 'bob@example.com', 0)")
    cursor.execute("INSERT OR IGNORE INTO orders (order_id, user_id, total_amount, status) VALUES (101, 1, 99.99, 'SHIPPED')")
    cursor.execute("INSERT OR IGNORE INTO legacy_metrics (metric_id, val_x, flag_y) VALUES (1, 0.5, 1)")
    
    conn.commit()
    conn.close()
    
    log_path = Path("data/usage_logs.sql")
    print(f"Creating mock logs at {log_path}...")
    with open(log_path, "w") as f:
        f.write("-- Application Query Logs\n")
        f.write("SELECT val_x FROM legacy_metrics WHERE val_x > 0.9; -- Monitoring CPU Load\n")
        f.write("SELECT * FROM legacy_metrics WHERE flag_y = 1; -- Check if system is DEPRECATED\n")

    print("Demo environment ready.")

if __name__ == "__main__":
    create_demo_db()