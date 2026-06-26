import sqlite3
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")  # Indian locale for realistic names/cities
random.seed(42)
Faker.seed(42)

DB_PATH = "data/ecommerce.db"

# ─────────────────────────────────────────────
# CONFIG — tweak these to scale up/down
# ─────────────────────────────────────────────
NUM_CUSTOMERS = 300
NUM_ORDERS = 2000
DATE_START = datetime(2024, 1, 1)
DATE_END = datetime(2025, 6, 25)

# ─────────────────────────────────────────────
# REFERENCE DATA
# ─────────────────────────────────────────────
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
]

PRODUCTS = [
    # (name, category, price, stock)
    # Electronics
    ("Wireless Mouse",          "Electronics",   799,   150),
    ("Mechanical Keyboard",     "Electronics",  2999,    75),
    ("USB-C Hub 7-in-1",        "Electronics",  1499,   200),
    ("Webcam HD 1080p",         "Electronics",  1999,    90),
    ("Noise Cancelling Earbuds","Electronics",  3499,   110),
    ("Bluetooth Speaker",       "Electronics",  1799,    80),
    ("Smartwatch Pro",          "Electronics",  8999,    45),
    ("Portable SSD 1TB",        "Electronics",  5499,    60),
    ("Ring Light 18 inch",      "Electronics",  2199,    95),
    ("Graphics Tablet",         "Electronics",  6999,    35),
    ("Laptop Stand Aluminium",  "Electronics",  1299,   180),
    ("USB Microphone",          "Electronics",  3999,    55),
    ("HDMI Cable 2m",           "Electronics",   399,   400),
    ("Power Bank 20000mAh",     "Electronics",  1999,   130),
    ("Wireless Charger Pad",    "Electronics",   999,   160),

    # Furniture
    ("Standing Desk 140cm",     "Furniture",   18999,   20),
    ("Ergonomic Chair",         "Furniture",   12999,   30),
    ("Monitor Arm Dual",        "Furniture",    3499,   50),
    ("3-Drawer Pedestal",       "Furniture",    5999,   25),
    ("Bookshelf 5-Tier",        "Furniture",    4499,   40),
    ("Sofa Cum Bed",            "Furniture",   22999,   15),
    ("Office Desk L-Shape",     "Furniture",   14999,   18),
    ("Bean Bag XL",             "Furniture",    3999,   60),

    # Accessories
    ("Monitor Light Bar",       "Accessories",  1299,  120),
    ("Desk Pad XL",             "Accessories",   699,  300),
    ("Cable Management Box",    "Accessories",   499,  250),
    ("Wrist Rest Gel",          "Accessories",   349,  200),
    ("Screen Cleaning Kit",     "Accessories",   249,  350),
    ("Cable Clips Pack 20",     "Accessories",   199,  500),
    ("Laptop Sleeve 15 inch",   "Accessories",   799,  180),
    ("Monitor Privacy Screen",  "Accessories",  1799,   70),

    # Stationery
    ("Bullet Journal A5",       "Stationery",    499,  400),
    ("Gel Pen Set 12pcs",       "Stationery",    299,  600),
    ("Sticky Notes Combo",      "Stationery",    199,  700),
    ("Document Organiser",      "Stationery",    649,  150),
    ("Whiteboard A2",           "Stationery",   1299,   80),
    ("Highlighter Set 6pcs",    "Stationery",    249,  500),
    ("Desk Organiser Bamboo",   "Stationery",    899,  130),

    # Clothing
    ("Polo T-Shirt",            "Clothing",      799,  300),
    ("Hoodie Zipper",           "Clothing",     1499,  200),
    ("Cargo Shorts",            "Clothing",      999,  180),
    ("Formal Shirt",            "Clothing",     1299,  160),
    ("Track Pants",             "Clothing",      899,  220),

    # Sports
    ("Yoga Mat Anti-Slip",      "Sports",        899,  200),
    ("Resistance Bands Set",    "Sports",        699,  250),
    ("Dumbbell 5kg Pair",       "Sports",       1999,   80),
    ("Jump Rope Speed",         "Sports",        499,  300),
    ("Water Bottle 1L",         "Sports",        599,  400),
    ("Foam Roller",             "Sports",        799,  150),
]

# Order status weighted distribution
ORDER_STATUSES = ["completed", "completed", "completed", "completed",
                  "completed", "completed",   # 60% completed
                  "shipped",  "shipped",  "shipped",  "shipped",  # 20% shipped
                  "pending",  "pending",  "pending",              # 15% pending
                  "cancelled"]                                     # 5% cancelled

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def random_date(start: datetime, end: datetime) -> str:
    """Return a random datetime string between start and end."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    dt = start + timedelta(seconds=random_seconds)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def weighted_customer_ids(num_customers: int, num_orders: int) -> list:
    """
    Simulate realistic purchase behaviour:
    - 10% VIP customers  → ~40% of orders
    - 30% regular        → ~40% of orders
    - 60% one-time       → ~20% of orders
    """
    vip_count     = max(1, int(num_customers * 0.10))
    regular_count = max(1, int(num_customers * 0.30))

    vip_ids     = list(range(1, vip_count + 1))
    regular_ids = list(range(vip_count + 1, vip_count + regular_count + 1))
    casual_ids  = list(range(vip_count + regular_count + 1, num_customers + 1))

    pool = (
        random.choices(vip_ids,     k=int(num_orders * 0.40)) +
        random.choices(regular_ids, k=int(num_orders * 0.40)) +
        random.choices(casual_ids,  k=int(num_orders * 0.20))
    )
    random.shuffle(pool)
    return pool[:num_orders]


# ─────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────
def create_tables(cursor):
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            city        TEXT    NOT NULL,
            signup_date TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            price       REAL    NOT NULL,
            stock       INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date  TEXT    NOT NULL,
            total       REAL    NOT NULL,
            status      TEXT    NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER NOT NULL,
            price       REAL    NOT NULL,
            FOREIGN KEY (order_id)   REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    """)


# ─────────────────────────────────────────────
# SEED FUNCTIONS
# ─────────────────────────────────────────────
def seed_customers(cursor):
    print("  Seeding customers...")
    customers = []
    emails_seen = set()

    while len(customers) < NUM_CUSTOMERS:
        name  = fake.name()
        email = fake.email()
        if email in emails_seen:
            continue
        emails_seen.add(email)
        city        = random.choice(CITIES)
        signup_date = random_date(DATE_START - timedelta(days=365), DATE_END)
        customers.append((name, email, city, signup_date))

    cursor.executemany(
        "INSERT OR IGNORE INTO customers (name, email, city, signup_date) VALUES (?, ?, ?, ?)",
        customers,
    )
    print(f"    [OK] {len(customers)} customers inserted")


def seed_products(cursor):
    print("  Seeding products...")
    cursor.executemany(
        "INSERT OR IGNORE INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        PRODUCTS,
    )
    print(f"    [OK] {len(PRODUCTS)} products inserted")


def seed_orders_and_items(cursor):
    print("  Seeding orders + order items...")

    # Fetch product ids and prices for item generation
    cursor.execute("SELECT id, category, price FROM products")
    all_products = cursor.fetchall()  # [(id, category, price), ...]

    # Category-based quantity rules (realistic)
    def pick_quantity(category: str) -> int:
        if category in ("Furniture",):
            return 1
        elif category in ("Electronics",):
            return random.choices([1, 2, 3], weights=[70, 25, 5])[0]
        elif category in ("Stationery", "Accessories", "Sports"):
            return random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
        else:
            return random.choices([1, 2, 3], weights=[60, 30, 10])[0]

    customer_ids = weighted_customer_ids(NUM_CUSTOMERS, NUM_ORDERS)

    orders_inserted = 0
    items_inserted  = 0

    for customer_id in customer_ids:
        order_date = random_date(DATE_START, DATE_END)
        status     = random.choice(ORDER_STATUSES)

        # Pick 1-4 distinct products per order
        num_items     = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
        chosen_prods  = random.sample(all_products, k=min(num_items, len(all_products)))

        line_items = []
        order_total = 0.0
        for prod_id, category, unit_price in chosen_prods:
            qty         = pick_quantity(category)
            line_total  = round(unit_price * qty, 2)
            order_total += line_total
            line_items.append((prod_id, qty, unit_price))

        order_total = round(order_total, 2)

        # Insert order
        cursor.execute(
            "INSERT INTO orders (customer_id, order_date, total, status) VALUES (?, ?, ?, ?)",
            (customer_id, order_date, order_total, status),
        )
        order_id = cursor.lastrowid
        orders_inserted += 1

        # Insert order items
        for prod_id, qty, unit_price in line_items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, prod_id, qty, unit_price),
            )
            items_inserted += 1

    print(f"    [OK] {orders_inserted} orders inserted")
    print(f"    [OK] {items_inserted} order items inserted")


# ─────────────────────────────────────────────
# STATS SUMMARY
# ─────────────────────────────────────────────
def print_summary(cursor):
    print("\n" + "-" * 45)
    print("  DATABASE SUMMARY")
    print("-" * 45)

    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"  Customers     : {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM products")
    print(f"  Products      : {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM orders")
    print(f"  Orders        : {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM order_items")
    print(f"  Order Items   : {cursor.fetchone()[0]}")

    cursor.execute("SELECT SUM(total) FROM orders WHERE status='completed'")
    revenue = cursor.fetchone()[0] or 0
    print(f"  Total Revenue : Rs.{revenue:,.2f}  (completed orders)")

    cursor.execute("""
        SELECT status, COUNT(*) as cnt
        FROM orders GROUP BY status ORDER BY cnt DESC
    """)
    print("\n  Order Status Breakdown:")
    for row in cursor.fetchall():
        print(f"    {row[0]:<12} -> {row[1]} orders")

    cursor.execute("""
        SELECT category, COUNT(*) as cnt
        FROM products GROUP BY category ORDER BY cnt DESC
    """)
    print("\n  Products by Category:")
    for row in cursor.fetchall():
        print(f"    {row[0]:<14} -> {row[1]} products")

    print("-" * 45)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    os.makedirs("data", exist_ok=True)

    # Fresh DB every run
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[DEL] Removed existing database: {DB_PATH}")

    print(f"\n[START] Creating database: {DB_PATH}\n")

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_tables(cursor)
    seed_customers(cursor)
    seed_products(cursor)
    seed_orders_and_items(cursor)

    conn.commit()
    print_summary(cursor)
    conn.close()

    print(f"\n[OK] Database ready at: {DB_PATH}")
    print("   Run: streamlit run app.py\n")


if __name__ == "__main__":
    main()