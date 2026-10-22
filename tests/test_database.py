import tempfile
import unittest
from pathlib import Path

from chicken_crave.database import ChickenCraveDB


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test.db"
        self.db = ChickenCraveDB(str(self.db_path))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_seeded_products_are_available(self):
        products = self.db.list_products()
        self.assertGreaterEqual(len(products), 8)

    def test_cart_persistence_and_total(self):
        product = self.db.list_products()[0]
        self.db.set_cart_quantity(product["id"], 2)

        items = self.db.get_cart_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 2)
        self.assertAlmostEqual(self.db.cart_total(), round(product["price"] * 2, 2))

    def test_place_order_moves_cart_items_to_history(self):
        products = self.db.list_products()[:2]
        self.db.set_cart_quantity(products[0]["id"], 1)
        self.db.set_cart_quantity(products[1]["id"], 2)

        order_id = self.db.place_order("Alex", "123 Main St")
        self.assertIsInstance(order_id, int)
        self.assertEqual(self.db.get_cart_items(), [])

        orders = self.db.get_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["id"], order_id)
        self.assertEqual(len(orders[0]["items"]), 2)

    def test_place_order_requires_name_and_address(self):
        product = self.db.list_products()[0]
        self.db.set_cart_quantity(product["id"], 1)

        with self.assertRaises(ValueError):
            self.db.place_order("", "address")


if __name__ == "__main__":
    unittest.main()
