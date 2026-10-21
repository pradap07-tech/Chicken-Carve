# Chicken-Carve

Chicken-Carve is a dark-themed glassmorphism food ordering application built with Flask and SQLite.

## Features

- 120 seeded food products across 24 categories
- Product catalog with search, category filtering, and sorting
- Cart interactions without forced navigation (add/update/remove)
- Checkout flow with persisted order history
- SQLite storage for products, cart state, orders, and order items
- Async/lazy image loading using a Web Worker with queue-based concurrency and fallback image support
- Responsive premium UI with smooth transitions

## Tech Stack

- Python 3.11+
- Flask 3
- SQLite (built-in)
- Vanilla JavaScript + CSS
- Pytest for integration tests

## Setup

1. Clone and enter the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python app.py
```

5. Open `http://127.0.0.1:5000` in your browser.

## Tests

Run:

```bash
pytest
```

## Environment

- Optional `CHICKEN_CARVE_DB` environment variable lets you choose a custom SQLite file path.

## Project Structure

- `app.py` – Flask routes and API layer
- `database.py` – SQLite schema, seeding, cart/order operations, error handling
- `seed_data.py` – 120-product seed data generation
- `templates/index.html` – App layout
- `static/app.js` – Product, cart, checkout, and order history client logic
- `static/imageWorker.js` – Background image downloader and cache queue
- `static/styles.css` – dark glassmorphism UI
- `tests/test_app.py` – key flow tests
