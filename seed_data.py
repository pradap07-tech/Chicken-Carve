from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class ProductSeed:
    name: str
    description: str
    price: float
    category: str
    image_url: str


CATEGORY_KEYWORDS = {
    "Chicken Specials": "grilled chicken",
    "Burgers": "burger",
    "Pizzas": "pizza",
    "Pastas": "pasta",
    "Rice Bowls": "rice bowl",
    "Wraps": "wrap",
    "Salads": "salad",
    "Seafood": "seafood",
    "Steaks": "steak",
    "Sandwiches": "sandwich",
    "Soups": "soup",
    "Desserts": "dessert",
    "Beverages": "beverage",
    "Breakfast": "breakfast",
    "Vegan": "vegan",
    "Indian": "indian food",
    "Mexican": "mexican food",
    "Chinese": "chinese food",
    "Japanese": "japanese food",
    "Mediterranean": "mediterranean food",
    "BBQ": "barbecue",
    "Snacks": "snack",
    "Healthy Meals": "healthy meal",
    "Family Combos": "family meal",
}

VARIANTS = [
    ("Classic", "A balanced and satisfying take on"),
    ("Spicy", "Turned up with bold spices and heat in"),
    ("Smoky", "Slow-cooked flavor with rich aroma in"),
    ("Deluxe", "Premium ingredients and chef finishing for"),
    ("House", "Our signature crowd-pleasing style of"),
]


def generate_products() -> list[ProductSeed]:
    products: list[ProductSeed] = []
    lock = 1

    for category_index, (category, keyword) in enumerate(CATEGORY_KEYWORDS.items()):
        base_price = 6.99 + category_index * 0.45
        for variant_index, (variant, desc_prefix) in enumerate(VARIANTS):
            price = round(base_price + (variant_index * 1.15), 2)
            name = f"{variant} {category}"
            description = f"{desc_prefix} {category.lower()} with fresh herbs and house sauces."
            image_query = quote_plus(f"{keyword},plate")
            image_url = f"https://loremflickr.com/640/480/{image_query}?lock={lock}"
            products.append(
                ProductSeed(
                    name=name,
                    description=description,
                    price=price,
                    category=category,
                    image_url=image_url,
                )
            )
            lock += 1

    return products
