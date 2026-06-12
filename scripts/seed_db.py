import sqlite3
import pandas as pd

CSV_PATH = "/Users/jayesh/ShoppingAgent/data/electronics_clean.csv"
DB_PATH = "products.db"

df=pd.read_csv(CSV_PATH)
print(f"rows: {len(df)}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

#Enabling foreign key enforcement(off by default) 
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL,
        image           TEXT,
        ratings         REAL,
        no_of_ratings   INTEGER,
        discount_price  REAL NOT NULL,
        actual_price    REAL,
        category_id     INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );
""")
print("Tables created or already exists.")

unique_categories = df["category"].dropna().unique()

cursor.executemany(
    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
    [(cat,) for cat in unique_categories]
)
print(f"Inserted {len(unique_categories)} categories")

# SELECT all categories we just inserted, store as { 'Smartphones': 1, ... }
cursor.execute("SELECT category_id, name FROM categories")
category_map = {name: cid for cid, name in cursor.fetchall()}


#inserting product values.
inserted = 0
skipped = 0

for _, row in df.iterrows():
    category_id = category_map.get(row["category"])

    if category_id is None:
        skipped += 1
        continue

    cursor.execute("""
        INSERT INTO products (name, image, ratings, no_of_ratings, discount_price, actual_price, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row["name"],
        row["image"],
        None if pd.isna(row["ratings"]) else float(row["ratings"]),
        None if pd.isna(row["no_of_ratings"]) else int(row["no_of_ratings"]),
        float(row["discount_price"]),
        None if pd.isna(row["actual_price"]) else float(row["actual_price"]),
        category_id
    ))
    inserted += 1

conn.commit()
conn.close()

print(f"\n{inserted} products inserted, {skipped} skipped")
print(f"Database saved to: {DB_PATH}")