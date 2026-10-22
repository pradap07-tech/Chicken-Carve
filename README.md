# Chicken Crave - 3-Tier Architecture

This application has been modularized from a single monolithic script into a clean **3-Tier Architecture**:

```
├── database.py       # Database Layer (SQLite schema, customer upsert, order storage & queries)
├── backend.py        # Backend Layer (Menu data, Cart manager, Image service, business validation)
├── frontend.py       # Frontend Layer (Tkinter GUI, custom Canvas widgets, cards, views & dialogs)
├── main.py           # Application Entry Point (Wires DB, Backend, and Frontend together)
└── Chicken Carve.py  # Backward-compatible launcher delegating to main.py
```

---

## Architecture Overview

### 1. Database Layer (`database.py`)
- **`DatabaseManager`**:
  - Connects to `chicken_crave.db` with `sqlite3.Row` and `PRAGMA foreign_keys = ON`.
  - Ensures relational tables: `customers`, `orders`, and `order_items`.
  - Atomically records customer details (`upsert_customer`) and orders with line items (`create_order`).
  - Fetches order history and line-item details (`get_orders_by_phone`, `get_order_items`).

### 2. Backend Layer (`backend.py`)
- **Catalog Data**: Defines `MENU` and `CATEGORIES`.
- **`Cart`**: Encapsulates cart state, quantity additions/decrements, total calculation, item counts, and clear.
- **`ImageService`**: Handles product image caching, remote downloading, and Pillow/Tk PhotoImage scaling.
- **`BackendService`**: Coordinates business logic:
  - Menu filtering and search (`get_filtered_menu`).
  - Validation of customer name, 10-digit mobile number, and address.
  - Order creation and transaction workflow (`place_order`).
  - History retrieval (`get_order_history`).

### 3. Frontend Layer (`frontend.py`)
- **Design Tokens**: Standardized colors (`RED`, `DARK`, `WHITE`, `BG`, `BORDER`, `MUTED`).
- **Custom Widgets**:
  - `RoundedHeaderButton`: Interactive canvas pill button.
  - `animated_button`: Canvas button with smooth hover fade.
- **Views & Components**:
  - Header with live badge counter and search bar.
  - Hero banner with canvas particle animations.
  - Scrollable category sidebar + responsive 3-column product grid with product cards.
  - Checkout page with cart modification, delivery form, and payment selection.
  - Order history modal with mobile number search and item inspector.

### 4. Entry Points
- **`main.py`**: The clean entry point to start the app.
- **`Chicken Carve.py`**: Kept for full backward compatibility; launches `main.py`.

---

## How to Run

Execute either:
```bash
python main.py
```
or:
```bash
python "Chicken Carve.py"
```
