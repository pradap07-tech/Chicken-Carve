"""SQLite persistence layer for Chicken Crave."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .products import DEFAULT_PRODUCTS


class ChickenCraveDB:
    def __init__(self, db_path: str = "chicken_crave.db") -> None:
        self.db_path = Path(db_path)
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _setup(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    image_url TEXT,
                    fallback_image TEXT NOT NULL,
                    description TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cart_items (
                    product_id INTEGER PRIMARY KEY,
                    quantity INTEGER NOT NULL CHECK(quantity >= 0),
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    total REAL NOT NULL,
                    placed_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    unit_price REAL NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY(product_id) REFERENCES products(id)
                );
                """
            )
            self._seed_products(conn)

    def _seed_products(self, conn: sqlite3.Connection) -> None:
        existing = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if existing:
            return

        conn.executemany(
            """
            INSERT INTO products (name, category, price, image_url, fallback_image, description)
            VALUES (:name, :category, :price, :image_url, :fallback_image, :description)
            """,
            DEFAULT_PRODUCTS,
        )

    def list_categories(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
        return [row[0] for row in rows]

    def list_products(self, query: str = "", category: str = "All") -> List[Dict]:
        statement = "SELECT * FROM products WHERE 1=1"
        params: List[object] = []

        if query:
            statement += " AND (name LIKE ? OR description LIKE ?)"
            search = f"%{query.strip()}%"
            params.extend([search, search])

        if category and category != "All":
            statement += " AND category = ?"
            params.append(category)

        statement += " ORDER BY category, name"

        with self._connect() as conn:
            rows = conn.execute(statement, params).fetchall()
        return [dict(row) for row in rows]

    def set_cart_quantity(self, product_id: int, quantity: int) -> None:
        quantity = max(0, int(quantity))
        with self._connect() as conn:
            if quantity == 0:
                conn.execute("DELETE FROM cart_items WHERE product_id = ?", (product_id,))
                return

            conn.execute(
                """
                INSERT INTO cart_items(product_id, quantity, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    quantity = excluded.quantity,
                    updated_at = excluded.updated_at
                """,
                (product_id, quantity, datetime.now(timezone.utc).isoformat()),
            )

    def get_cart_items(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT p.*, c.quantity, ROUND(p.price * c.quantity, 2) AS subtotal
                FROM cart_items c
                JOIN products p ON p.id = c.product_id
                WHERE c.quantity > 0
                ORDER BY c.updated_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def cart_total(self) -> float:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT ROUND(COALESCE(SUM(p.price * c.quantity), 0), 2)
                FROM cart_items c
                JOIN products p ON p.id = c.product_id
                WHERE c.quantity > 0
                """
            ).fetchone()
        return float(row[0] if row else 0.0)

    def clear_cart(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM cart_items")

    def place_order(self, customer_name: str, address: str) -> Optional[int]:
        customer_name = customer_name.strip()
        address = address.strip()
        if not customer_name or not address:
            raise ValueError("Customer name and address are required.")

        with self._connect() as conn:
            cart_rows = conn.execute(
                """
                SELECT c.product_id, c.quantity, p.price
                FROM cart_items c
                JOIN products p ON p.id = c.product_id
                WHERE c.quantity > 0
                """
            ).fetchall()
            if not cart_rows:
                return None

            total = round(sum(float(row["price"]) * int(row["quantity"]) for row in cart_rows), 2)
            cursor = conn.execute(
                """
                INSERT INTO orders(customer_name, address, total, placed_at)
                VALUES (?, ?, ?, ?)
                """,
                (customer_name, address, total, datetime.now(timezone.utc).isoformat()),
            )
            order_id = int(cursor.lastrowid)

            conn.executemany(
                """
                INSERT INTO order_items(order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (order_id, int(row["product_id"]), int(row["quantity"]), float(row["price"]))
                    for row in cart_rows
                ],
            )
            conn.execute("DELETE FROM cart_items")
            return order_id

    def get_orders(self) -> List[Dict]:
        with self._connect() as conn:
            orders = conn.execute(
                "SELECT * FROM orders ORDER BY placed_at DESC"
            ).fetchall()
            grouped: List[Dict] = []
            for order in orders:
                items = conn.execute(
                    """
                    SELECT oi.quantity, oi.unit_price, p.name
                    FROM order_items oi
                    JOIN products p ON p.id = oi.product_id
                    WHERE oi.order_id = ?
                    ORDER BY oi.id ASC
                    """,
                    (order["id"],),
                ).fetchall()
                grouped.append(
                    {
                        "id": order["id"],
                        "customer_name": order["customer_name"],
                        "address": order["address"],
                        "total": order["total"],
                        "placed_at": order["placed_at"],
                        "items": [dict(item) for item in items],
                    }
                )

        return grouped
