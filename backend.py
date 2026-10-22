from datetime import datetime
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import urllib.request

from database import DatabaseManager

MENU = [
    {
        "name": "Double Chicken Dynamite",
        "category": "Double Chicken Dynamite",
        "price": 349,
        "emoji": "🍔",
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60",
        "desc": "Two crispy chicken fillets with spicy dynamite sauce"
    },
    {
        "name": "Double Chicken Dynamite Combo",
        "category": "Double Chicken Dynamite",
        "price": 399,
        "emoji": "🍔🥤",
        "image": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&auto=format&fit=crop&q=60",
        "desc": "Dynamite burger with a chilled drink"
    },
    {
        "name": "Double Chicken Dynamite Meal",
        "category": "Double Chicken Dynamite",
        "price": 489,
        "emoji": "🍔🍟🥤",
        "image": "https://images.unsplash.com/photo-1610440042657-612c34d95e9f?w=500&auto=format&fit=crop&q=60",
        "desc": "Burger, golden fries and a refreshing drink"
    },
    {
        "name": "Double Chicken Dynamite Snack Box",
        "category": "Double Chicken Dynamite",
        "price": 499,
        "emoji": "🍔🍗",
        "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60",
        "desc": "Burger with crunchy chicken snacks and a drink"
    },
    {
        "name": "Double Chicken Dynamite Box Meal",
        "category": "Double Chicken Dynamite",
        "price": 569,
        "emoji": "🍔🍟🍗",
        "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60",
        "desc": "A loaded box meal for a bigger appetite"
    },
    {
        "name": "Wednesday Specials",
        "category": "Wednesday Specials",
        "price": 299,
        "emoji": "🍗🥤",
        "image": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500&auto=format&fit=crop&q=60",
        "desc": "A special chicken combo at a great price"
    },
    {
        "name": "Super Wednesday Feast",
        "category": "Wednesday Specials",
        "price": 499,
        "emoji": "🍗🍟🥤",
        "image": "https://images.unsplash.com/photo-1587314168485-3236d6710814?w=500&auto=format&fit=crop&q=60",
        "desc": "8 pieces of crunchy chicken tenders with spicy dips and drinks"
    },
    {
        "name": "Bucket for One",
        "category": "Buckets",
        "price": 299,
        "emoji": "🪣🍗",
        "image": "https://images.unsplash.com/photo-1513639776629-7b61b0ac49cb?w=500&auto=format&fit=crop&q=60",
        "desc": "A personal bucket of crispy chicken"
    },
    {
        "name": "Chicken Bucket - 6 pc",
        "category": "Buckets",
        "price": 599,
        "emoji": "🍗🍗",
        "image": "https://images.unsplash.com/photo-1569058242253-92a9c755a0ec?w=500&auto=format&fit=crop&q=60",
        "desc": "Six pieces of signature crispy chicken"
    },
    {
        "name": "Ultimate Family Bucket - 12 pc",
        "category": "Buckets",
        "price": 1099,
        "emoji": "🪣🍗🔥",
        "image": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=500&auto=format&fit=crop&q=60",
        "desc": "12 pieces of hot and crispy chicken for sharing"
    },
    {
        "name": "Smoky Grilled Chicken Bucket",
        "category": "Buckets",
        "price": 649,
        "emoji": "🍗🔥",
        "image": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=500&auto=format&fit=crop&q=60",
        "desc": "Slow-grilled tender chicken with bold smoky seasoning"
    },
    {
        "name": "Gold Edition Burger",
        "category": "Gold Edition",
        "price": 279,
        "emoji": "🍔",
        "image": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=500&auto=format&fit=crop&q=60",
        "desc": "A rich and satisfying premium burger"
    },
    {
        "name": "Gold Truffle Bacon Burger",
        "category": "Gold Edition",
        "price": 329,
        "emoji": "🍔🥓",
        "image": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=500&auto=format&fit=crop&q=60",
        "desc": "Crispy chicken fillet with truffle aioli and crispy smoked bacon strip"
    },
    {
        "name": "Chicken Zinger Burger",
        "category": "Burgers",
        "price": 199,
        "emoji": "🍔",
        "image": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=500&auto=format&fit=crop&q=60",
        "desc": "Crispy chicken, lettuce and signature sauce"
    },
    {
        "name": "Classic Veg Burger",
        "category": "Burgers",
        "price": 149,
        "emoji": "🥬🍔",
        "image": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?w=500&auto=format&fit=crop&q=60",
        "desc": "Crunchy veg patty with fresh lettuce"
    },
    {
        "name": "Spicy Peri-Peri Paneer Burger",
        "category": "Burgers",
        "price": 189,
        "emoji": "🧀🍔",
        "image": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=500&auto=format&fit=crop&q=60",
        "desc": "Thick fried cottage cheese patty tossed in fiery peri-peri spices"
    },
    {
        "name": "Tandoori Chicken Burger",
        "category": "Burgers",
        "price": 219,
        "emoji": "🍔🇮🇳",
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60",
        "desc": "Grilled chicken patty infused with smoky Indian tandoori spices and mint mayo"
    },
    {
        "name": "Chicken Rice Bowl",
        "category": "Rice Bowlz",
        "price": 229,
        "emoji": "🍚",
        "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60",
        "desc": "A hearty chicken rice bowl"
    },
    {
        "name": "Veg Fiery Rice Bowl",
        "category": "Rice Bowlz",
        "price": 189,
        "emoji": "🍚🥦",
        "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop&q=60",
        "desc": "Aromatic seasoned rice topped with crispy veg bites and hot garlic gravy"
    },
    {
        "name": "Classic Box Meal",
        "category": "Box-Meals",
        "price": 429,
        "emoji": "🍱🍗",
        "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60",
        "desc": "Chicken, fries and a drink in one box"
    },
    {
        "name": "All-Star Non-Veg Box",
        "category": "Box-Meals",
        "price": 469,
        "emoji": "🍱🍗🥤",
        "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60",
        "desc": "Zinger burger, 1 pc hot chicken, regular fries, and a chilled beverage"
    },
    {
        "name": "Chicken Roll",
        "category": "Rolls",
        "price": 169,
        "emoji": "🌯",
        "image": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=500&auto=format&fit=crop&q=60",
        "desc": "A flavour-packed chicken roll"
    },
    {
        "name": "Crispy Veggie Wrap",
        "category": "Rolls",
        "price": 139,
        "emoji": "🌯🥗",
        "image": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=500&auto=format&fit=crop&q=60",
        "desc": "Golden herb tortilla rolled with fresh greens, spicy potatoes, and eggless mayo"
    },
    {
        "name": "Chicken Popcorn",
        "category": "Snacks",
        "price": 179,
        "emoji": "🍿",
        "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60",
        "desc": "Bite-sized crispy chicken pieces"
    },
    {
        "name": "Peri Peri Fries",
        "category": "Snacks",
        "price": 119,
        "emoji": "🍟",
        "image": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=500&auto=format&fit=crop&q=60",
        "desc": "Golden fries with spicy seasoning"
    },
    {
        "name": "Crispy Chicken Strips (4 pc)",
        "category": "Snacks",
        "price": 169,
        "emoji": "🍗",
        "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60",
        "desc": "Boneless, extra crunchy hand-breaded chicken tenders"
    },
    {
        "name": "Cheesy Jalapeño Poppers",
        "category": "Snacks",
        "price": 139,
        "emoji": "🧀🌶️",
        "image": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=60",
        "desc": "Crispy golden bites filled with molten cheese and sliced jalapeños"
    },
    {
        "name": "Pepsi",
        "category": "Beverages & Desserts",
        "price": 59,
        "emoji": "🥤",
        "image": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=500&auto=format&fit=crop&q=60",
        "desc": "Chilled fizzy drink"
    },
    {
        "name": "Chocolate Brownie",
        "category": "Beverages & Desserts",
        "price": 99,
        "emoji": "🍫",
        "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=60",
        "desc": "Rich chocolate brownie"
    },
    {
        "name": "Iced Lemon Tea",
        "category": "Beverages & Desserts",
        "price": 79,
        "emoji": "🍋🧃",
        "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=500&auto=format&fit=crop&q=60",
        "desc": "Refreshing chilled black tea infused with real lemon pulp"
    },
    {
        "name": "Belgian Chocolate Shake",
        "category": "Beverages & Desserts",
        "price": 149,
        "emoji": "🥤🍫",
        "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=60",
        "desc": "Thick milkshake blended with premium dark Belgian chocolate syrup"
    }
]

CATEGORIES = [
    ("Double Chicken Dynamite", "🍔"),
    ("Wednesday Specials", "🎉"),
    ("Buckets", "🪣"),
    ("Gold Edition", "👑"),
    ("Burgers", "🍔"),
    ("Rice Bowlz", "🍚"),
    ("Box-Meals", "🍱"),
    ("Rolls", "🌯"),
    ("Snacks", "🍗"),
    ("Beverages & Desserts", "🥤"),
]


class Cart:
    def __init__(self):
        self._items: Dict[str, Dict[str, Any]] = {}

    def add(self, item: Dict[str, Any]) -> None:
        name = item["name"]
        if name in self._items:
            self._items[name]["qty"] += 1
        else:
            self._items[name] = {**item, "qty": 1}

    def change_qty(self, name: str, delta: int) -> None:
        if name in self._items:
            self._items[name]["qty"] += delta
            if self._items[name]["qty"] <= 0:
                del self._items[name]

    def remove(self, name: str) -> None:
        if name in self._items:
            del self._items[name]

    def get_items(self) -> Dict[str, Dict[str, Any]]:
        return self._items

    def get_total(self) -> float:
        return sum(item["price"] * item["qty"] for item in self._items.values())

    def get_count(self) -> int:
        return sum(item["qty"] for item in self._items.values())

    def clear(self) -> None:
        self._items.clear()

    def is_empty(self) -> bool:
        return len(self._items) == 0


class ImageService:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent
        self.cache_dir = self.base_dir / "product_images"
        self.cache_dir.mkdir(exist_ok=True)
        self.image_cache: Dict[Tuple[str, Tuple[int, int]], Any] = {}

    def get_image(self, item: Dict[str, Any], max_size: Tuple[int, int] = (220, 205)):
        image_path = item.get("image", "").strip()
        if not image_path:
            return None

        if image_path.startswith(("https://", "http://")):
            suffix = Path(image_path.split("?", 1)[0]).suffix or ".jpg"
            filename = hashlib.md5(image_path.encode("utf-8")).hexdigest() + suffix
            full_path = self.cache_dir / filename
            if not full_path.exists():
                try:
                    request = urllib.request.Request(
                        image_path, headers={"User-Agent": "ChickenCrave/1.0"}
                    )
                    with urllib.request.urlopen(request, timeout=2.0) as response:
                        full_path.write_bytes(response.read())
                except Exception:
                    return None
        else:
            full_path = self.base_dir / image_path

        if not full_path.is_file():
            return None

        cache_key = (str(full_path), max_size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        photo = None
        try:
            from PIL import Image, ImageTk
            with Image.open(full_path) as source:
                source = source.convert("RGBA")
                source.thumbnail(max_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(source)
        except ImportError:
            try:
                import tkinter as tk
                photo = tk.PhotoImage(file=str(full_path))
                factor = max(
                    1,
                    (photo.width() + max_size[0] - 1) // max_size[0],
                    (photo.height() + max_size[1] - 1) // max_size[1]
                )
                if factor > 1:
                    photo = photo.subsample(factor, factor)
            except Exception:
                return None
        except Exception:
            return None

        if photo is not None:
            self.image_cache[cache_key] = photo
        return photo


class BackendService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.cart = Cart()
        self.images = ImageService()

    def get_categories(self) -> List[Tuple[str, str]]:
        return CATEGORIES

    def get_filtered_menu(self, active_category: Optional[str] = None, query: str = "") -> List[Dict[str, Any]]:
        clean_query = query.strip().lower()
        if clean_query == "search menu...":
            clean_query = ""

        return [
            item for item in MENU
            if (clean_query or item["category"] == active_category)
            and (
                not clean_query
                or clean_query in item["name"].lower()
                or clean_query in item["desc"].lower()
                or clean_query in item["category"].lower()
            )
        ]

    def validate_customer_details(self, name: str, phone: str, address: str) -> Tuple[bool, Optional[str]]:
        name = name.strip()
        phone = phone.strip()
        address = address.strip()

        if not name or not phone or not address:
            return False, "Please fill in all delivery details."
        if not phone.isdigit() or len(phone) != 10:
            return False, "Enter a valid 10-digit mobile number."
        return True, None

    def place_order(
        self,
        name: str,
        phone: str,
        address: str,
        payment_method: str = "Cash on Delivery"
    ) -> Dict[str, Any]:
        valid, err = self.validate_customer_details(name, phone, address)
        if not valid:
            return {"success": False, "error": err}

        if self.cart.is_empty():
            return {"success": False, "error": "Your cart is empty."}

        total = self.cart.get_total()
        order_code = "CC" + datetime.now().strftime("%y%m%d%H%M%S%f")
        order_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        items = list(self.cart.get_items().values())

        try:
            customer_id = self.db.upsert_customer(name.strip(), phone.strip(), address.strip())
            order_id = self.db.create_order(
                customer_id=customer_id,
                order_code=order_code,
                order_date=order_date,
                total=total,
                payment_method=payment_method,
                items=items,
                status="Placed"
            )
            self.cart.clear()
            return {
                "success": True,
                "order_id": order_id,
                "order_code": order_code,
                "customer_name": name.strip(),
                "total": total,
                "date": order_date
            }
        except Exception as exc:
            return {"success": False, "error": f"Database error: {exc}"}

    def get_order_history(self, phone: str) -> Tuple[bool, Any]:
        clean_phone = phone.strip()
        if not clean_phone.isdigit() or len(clean_phone) != 10:
            return False, "Enter a valid 10-digit mobile number."
        try:
            records = self.db.get_orders_by_phone(clean_phone)
            return True, records
        except Exception as exc:
            return False, str(exc)

    def get_order_items(self, order_id: int) -> List[Any]:
        try:
            return self.db.get_order_items(order_id)
        except Exception:
            return []
