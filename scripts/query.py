import sqlite3

conn = sqlite3.connect("/Users/jayesh/ShoppingAgent/database/products.db")
cursor = conn.cursor()

# cursor.execute("""
#     select c.name, avg(p.discount_price) from products p join categories c on p.category_id=c.category_id
#     group by c.name having avg(p.discount_price)>1000 order by p.discount_price desc
# """)
cursor.execute("""
    select * from categories
""")
for row in cursor.fetchall():
    print(row)
cursor.execute("PRAGMA table_info('products')")
cursor.execute("PRAGMA table_info('categories')")
for row in cursor.fetchall():
    print(row)

conn.close()