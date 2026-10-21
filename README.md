# Chicken Crave

Chicken Crave is a modern desktop food-ordering application built with **Python + Tkinter** and **SQLite**.

## Features

- Home, Menu, Cart, and Orders navigation
- Product catalog with categories and search/filtering
- Individual product images with:
  - background image downloading (never on UI thread)
  - bounded concurrent downloads
  - in-memory + on-disk caching
  - lazy loading while cards render
  - local fallback image per product
- Shopping cart with quantity controls
- Checkout flow with input validation
- Order history
- Persistent SQLite-backed cart and order storage

## Tech Stack

- Python 3.10+
- Tkinter (standard library)
- SQLite (standard library)
- Pillow (image decoding/resizing)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

The app creates `chicken_crave.db` in the project root and reuses it between runs.

## Tests

Run targeted persistence tests:

```bash
python -m unittest tests/test_database.py -v
```
