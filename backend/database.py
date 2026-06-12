import sqlite3

DB_PATH = "/Users/jayesh/ShoppingAgent/database/products.db" 

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # makes rows behave like dicts. Without it, sqlite3 returns plain tuples like (1, "Phone", 999).
    # With it, we can write row["name"] instead of row[1].
    conn.row_factory = sqlite3.Row
    return conn