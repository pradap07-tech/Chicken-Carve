from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from seed_data import generate_products

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "chicken_carve.db"


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""


class Database:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = str(db_path)
        self._lock = threading.Lock()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            raise DatabaseError(str(exc)) from exc
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    image_url TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cart_items (
                    product_id INTEGER PRIMARY KEY,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    notes TEXT,
                    subtotal REAL NOT NULL,
                    total REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    line_total REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
                """
            )

        self.seed_products_if_needed()

    def seed_products_if_needed(self) -> None:
        with self.connection() as conn:
            existing_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            if existing_count >= 120:
                return

            products = generate_products()
            conn.executemany(
                """
                INSERT INTO products (name, description, price, category, image_url)
                VALUES (:name, :description, :price, :category, :image_url)
                """,
                [product.__dict__ for product in products],
            )

    def get_categories(self) -> list[str]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT category FROM products ORDER BY category ASC"
            ).fetchall()
            return [row["category"] for row in rows]

    def list_products(
        self,
        search: str = "",
        category: str = "",
        sort_by: str = "name_asc",
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: dict[str, Any] = {}

        if search:
            clauses.append("(name LIKE :search OR description LIKE :search)")
            params["search"] = f"%{search.strip()}%"

        if category:
            clauses.append("category = :category")
            params["category"] = category.strip()

        order_map = {
            "name_asc": "name COLLATE NOCASE ASC",
            "name_desc": "name COLLATE NOCASE DESC",
            "price_asc": "price ASC",
            "price_desc": "price DESC",
            "category_asc": "category COLLATE NOCASE ASC, name COLLATE NOCASE ASC",
        }
        order_sql = order_map.get(sort_by, order_map["name_asc"])

        query = "SELECT id, name, description, price, category, image_url FROM products"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += f" ORDER BY {order_sql}"

        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_cart(self) -> dict[str, Any]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT p.id, p.name, p.price, p.image_url, ci.quantity,
                       ROUND(p.price * ci.quantity, 2) AS line_total
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                ORDER BY ci.updated_at DESC
                """
            ).fetchall()

        items = [dict(row) for row in rows]
        subtotal = round(sum(item["line_total"] for item in items), 2)
        delivery_fee = 4.99 if items else 0
        total = round(subtotal + delivery_fee, 2)
        return {
            "items": items,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": total,
            "count": sum(item["quantity"] for item in items),
        }

    def add_to_cart(self, product_id: int, quantity: int = 1) -> None:
        with self._lock, self.connection() as conn:
            conn.execute(
                """
                INSERT INTO cart_items(product_id, quantity, updated_at)
                VALUES (:product_id, :quantity, CURRENT_TIMESTAMP)
                ON CONFLICT(product_id)
                DO UPDATE SET quantity = quantity + :quantity,
                              updated_at = CURRENT_TIMESTAMP
                """,
                {"product_id": product_id, "quantity": max(1, quantity)},
            )

    def update_cart_item(self, product_id: int, quantity: int) -> None:
        with self._lock, self.connection() as conn:
            if quantity <= 0:
                conn.execute("DELETE FROM cart_items WHERE product_id = ?", (product_id,))
                return

            conn.execute(
                """
                UPDATE cart_items
                SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE product_id = ?
                """,
                (quantity, product_id),
            )

    def remove_cart_item(self, product_id: int) -> None:
        with self._lock, self.connection() as conn:
            conn.execute("DELETE FROM cart_items WHERE product_id = ?", (product_id,))

    def clear_cart(self) -> None:
        with self._lock, self.connection() as conn:
            conn.execute("DELETE FROM cart_items")

    def checkout(
        self,
        customer_name: str,
        address: str,
        phone: str,
        notes: str = "",
    ) -> dict[str, Any]:
        cart = self.get_cart()
        if not cart["items"]:
            raise DatabaseError("Cart is empty.")

        with self._lock, self.connection() as conn:
            order_cursor = conn.execute(
                """
                INSERT INTO orders (customer_name, address, phone, notes, subtotal, total)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_name.strip(),
                    address.strip(),
                    phone.strip(),
                    notes.strip(),
                    cart["subtotal"],
                    cart["total"],
                ),
            )
            order_id = order_cursor.lastrowid

            conn.executemany(
                """
                INSERT INTO order_items(order_id, product_id, name, price, quantity, line_total)
                VALUES (:order_id, :product_id, :name, :price, :quantity, :line_total)
                """,
                [
                    {
                        "order_id": order_id,
                        "product_id": item["id"],
                        "name": item["name"],
                        "price": item["price"],
                        "quantity": item["quantity"],
                        "line_total": item["line_total"],
                    }
                    for item in cart["items"]
                ],
            )

            conn.execute("DELETE FROM cart_items")

        return self.get_order(order_id)

    def get_orders(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            order_rows = conn.execute(
                """
                SELECT id, customer_name, address, phone, notes, subtotal, total, created_at
                FROM orders
                ORDER BY datetime(created_at) DESC
                """
            ).fetchall()

            orders: list[dict[str, Any]] = []
            for order_row in order_rows:
                item_rows = conn.execute(
                    """
                    SELECT product_id, name, price, quantity, line_total
                    FROM order_items
                    WHERE order_id = ?
                    ORDER BY id ASC
                    """,
                    (order_row["id"],),
                ).fetchall()
                order = dict(order_row)
                order["items"] = [dict(item_row) for item_row in item_rows]
                orders.append(order)

        return orders

    def get_order(self, order_id: int) -> dict[str, Any]:
        with self.connection() as conn:
            order_row = conn.execute(
                """
                SELECT id, customer_name, address, phone, notes, subtotal, total, created_at
                FROM orders
                WHERE id = ?
                """,
                (order_id,),
            ).fetchone()
            if order_row is None:
                raise DatabaseError("Order not found")

            item_rows = conn.execute(
                """
                SELECT product_id, name, price, quantity, line_total
                FROM order_items
                WHERE order_id = ?
                ORDER BY id ASC
                """,
                (order_id,),
            ).fetchall()

        order = dict(order_row)
        order["items"] = [dict(item_row) for item_row in item_rows]
        return order
