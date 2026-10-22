import sqlite3
from typing import List, Optional, Dict, Any


class DatabaseManager:
    def __init__(self, db_path: str = "chicken_crave.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self.connect()
        self.initialize_database()

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            return self.connect()
        return self._conn

    def initialize_database(self) -> None:
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    address TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_code TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    total REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Placed',
                    FOREIGN KEY(customer_id) REFERENCES customers(id)
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id)
                )
            """)

    def upsert_customer(self, name: str, phone: str, address: str) -> int:
        with self.conn:
            existing = self.conn.execute(
                "SELECT id FROM customers WHERE phone = ?", (phone,)
            ).fetchone()
            if existing:
                customer_id = existing["id"]
                self.conn.execute(
                    "UPDATE customers SET name = ?, address = ? WHERE id = ?",
                    (name, address, customer_id)
                )
                return customer_id
            else:
                cursor = self.conn.execute(
                    "INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)",
                    (name, phone, address)
                )
                return cursor.lastrowid

    def create_order(
        self,
        customer_id: int,
        order_code: str,
        order_date: str,
        total: float,
        payment_method: str,
        items: List[Dict[str, Any]],
        status: str = "Placed"
    ) -> int:
        with self.conn:
            cursor = self.conn.execute("""
                INSERT INTO orders (order_code, customer_id, order_date, total, payment_method, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_code, customer_id, order_date, total, payment_method, status))
            order_id = cursor.lastrowid

            self.conn.executemany("""
                INSERT INTO order_items (order_id, product_name, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, [
                (order_id, item["name"], item["qty"], item["price"])
                for item in items
            ])
            return order_id

    def get_orders_by_phone(self, phone: str) -> List[sqlite3.Row]:
        return self.conn.execute("""
            SELECT o.id, o.order_code, o.order_date, o.total, o.payment_method, o.status
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            WHERE c.phone = ?
            ORDER BY o.id DESC
        """, (phone,)).fetchall()

    def get_order_items(self, order_id: int) -> List[sqlite3.Row]:
        return self.conn.execute("""
            SELECT product_name, quantity, unit_price
            FROM order_items
            WHERE order_id = ?
        """, (order_id,)).fetchall()

    def close(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            finally:
                self._conn = None
