from __future__ import annotations

from http import HTTPStatus
from os import getenv

from flask import Flask, jsonify, render_template, request

from database import Database, DatabaseError


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    db_path = app.config.get("DATABASE") or getenv("CHICKEN_CARVE_DB")
    db = Database(db_path) if db_path else Database()
    db.init_db()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/products")
    def products():
        search = request.args.get("search", "", type=str)
        category = request.args.get("category", "", type=str)
        sort_by = request.args.get("sort", "name_asc", type=str)

        results = db.list_products(search=search, category=category, sort_by=sort_by)
        return jsonify({"products": results})

    @app.get("/api/categories")
    def categories():
        return jsonify({"categories": db.get_categories()})

    @app.get("/api/cart")
    def cart():
        return jsonify(db.get_cart())

    @app.post("/api/cart/add")
    def add_to_cart():
        payload = request.get_json(silent=True) or {}
        product_id = payload.get("product_id")
        quantity = payload.get("quantity", 1)

        if not isinstance(product_id, int) or not isinstance(quantity, int):
            return jsonify({"error": "Invalid cart payload."}), HTTPStatus.BAD_REQUEST

        try:
            db.add_to_cart(product_id=product_id, quantity=quantity)
            return jsonify(db.get_cart()), HTTPStatus.CREATED
        except DatabaseError as exc:
            return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST

    @app.patch("/api/cart/<int:product_id>")
    def update_cart_item(product_id: int):
        payload = request.get_json(silent=True) or {}
        quantity = payload.get("quantity")
        if not isinstance(quantity, int):
            return jsonify({"error": "Quantity must be an integer."}), HTTPStatus.BAD_REQUEST

        try:
            db.update_cart_item(product_id=product_id, quantity=quantity)
            return jsonify(db.get_cart())
        except DatabaseError as exc:
            return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST

    @app.delete("/api/cart/<int:product_id>")
    def remove_from_cart(product_id: int):
        try:
            db.remove_cart_item(product_id)
            return jsonify(db.get_cart())
        except DatabaseError as exc:
            return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST

    @app.post("/api/checkout")
    def checkout():
        payload = request.get_json(silent=True) or {}
        customer_name = (payload.get("customer_name") or "").strip()
        address = (payload.get("address") or "").strip()
        phone = (payload.get("phone") or "").strip()
        notes = (payload.get("notes") or "").strip()

        if not customer_name or not address or not phone:
            return (
                jsonify({"error": "Customer name, address, and phone are required."}),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            order = db.checkout(
                customer_name=customer_name,
                address=address,
                phone=phone,
                notes=notes,
            )
            return jsonify(order), HTTPStatus.CREATED
        except DatabaseError as exc:
            return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST

    @app.get("/api/orders")
    def orders():
        try:
            return jsonify({"orders": db.get_orders()})
        except DatabaseError as exc:
            return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception):
        return jsonify({"error": f"Unexpected error: {exc}"}), HTTPStatus.INTERNAL_SERVER_ERROR

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
