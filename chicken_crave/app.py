"""Tkinter desktop app entrypoint for Chicken Crave."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .database import ChickenCraveDB
from .image_loader import AsyncImageLoader


class ChickenCraveApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chicken Crave")
        self.geometry("1160x760")
        self.minsize(980, 620)
        self.configure(bg="#090b13")

        self.db = ChickenCraveDB()
        self.asset_dir = Path(__file__).resolve().parent / "assets"
        self.image_loader = AsyncImageLoader(self, cache_dir=str(Path(".image_cache")), max_workers=4)

        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All")
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()

        self._build_shell()
        self.show_home()

    def _build_shell(self):
        top = tk.Frame(self, bg="#0f1426", height=72)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top,
            text="Chicken Crave",
            bg="#0f1426",
            fg="#f4f6ff",
            font=("Segoe UI", 20, "bold"),
        ).pack(side="left", padx=20)

        nav = tk.Frame(top, bg="#0f1426")
        nav.pack(side="right", padx=16)
        self.nav_buttons = {}
        for text, action in [
            ("Home", self.show_home),
            ("Menu", self.show_menu),
            ("Cart", self.show_cart),
            ("Orders", self.show_orders),
        ]:
            btn = tk.Button(
                nav,
                text=text,
                command=action,
                bg="#1c2340",
                fg="#f4f6ff",
                activebackground="#2b3a64",
                activeforeground="#ffffff",
                bd=0,
                relief="flat",
                padx=18,
                pady=10,
                font=("Segoe UI", 11, "bold"),
                cursor="hand2",
            )
            btn.pack(side="left", padx=8)
            self._add_hover(btn, "#1c2340", "#2f3f6e")
            self.nav_buttons[text] = btn

        self.content = tk.Frame(self, bg="#090b13")
        self.content.pack(fill="both", expand=True)

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _set_active_nav(self, active_name: str):
        for name, button in self.nav_buttons.items():
            button.configure(bg="#3550b5" if name == active_name else "#1c2340")

    def show_home(self):
        self._clear_content()
        self._set_active_nav("Home")

        hero = tk.Frame(self.content, bg="#121b35", padx=24, pady=24)
        hero.pack(fill="x", padx=20, pady=20)

        tk.Label(
            hero,
            text="Premium chicken meals, crafted and delivered fresh.",
            bg="#121b35",
            fg="#f6f7ff",
            font=("Segoe UI", 24, "bold"),
            wraplength=900,
            justify="left",
        ).pack(anchor="w")

        tk.Label(
            hero,
            text="Explore chef-crafted mains, wraps, starters, and drinks in a sleek ordering experience.",
            bg="#121b35",
            fg="#b6bfd8",
            font=("Segoe UI", 12),
        ).pack(anchor="w", pady=(8, 0))

        section = tk.Frame(self.content, bg="#090b13")
        section.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        tk.Label(
            section,
            text="Featured items",
            bg="#090b13",
            fg="#f0f2ff",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        products = self.db.list_products()[:4]
        grid = tk.Frame(section, bg="#090b13")
        grid.pack(fill="both", expand=True)
        self._render_product_grid(grid, products, columns=4)

    def show_menu(self):
        self._clear_content()
        self._set_active_nav("Menu")

        filters = tk.Frame(self.content, bg="#090b13")
        filters.pack(fill="x", padx=20, pady=(20, 8))

        search_entry = tk.Entry(
            filters,
            textvariable=self.search_var,
            bg="#151b31",
            fg="#f4f6ff",
            insertbackground="#f4f6ff",
            relief="flat",
            font=("Segoe UI", 11),
            width=40,
        )
        search_entry.pack(side="left", padx=(0, 12), ipady=8)
        search_entry.bind("<KeyRelease>", lambda _e: self.refresh_menu_products())

        categories = ["All", *self.db.list_categories()]
        category_menu = ttk.Combobox(
            filters,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=20,
        )
        category_menu.pack(side="left")
        category_menu.bind("<<ComboboxSelected>>", lambda _e: self.refresh_menu_products())

        refresh_btn = tk.Button(
            filters,
            text="Clear Filters",
            command=self._clear_filters,
            bg="#24336b",
            fg="#f4f6ff",
            activebackground="#3550b5",
            bd=0,
            padx=16,
            pady=9,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
        )
        refresh_btn.pack(side="left", padx=12)
        self._add_hover(refresh_btn, "#24336b", "#3550b5")

        self.menu_scroll = self._make_scroll_frame(self.content)
        self.menu_scroll.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        self.refresh_menu_products()

    def _clear_filters(self):
        self.search_var.set("")
        self.category_var.set("All")
        self.refresh_menu_products()

    def refresh_menu_products(self):
        container = self.menu_scroll["inner"]
        for child in container.winfo_children():
            child.destroy()
        products = self.db.list_products(query=self.search_var.get(), category=self.category_var.get())
        self._render_product_grid(container, products, columns=3)

    def _render_product_grid(self, parent, products, columns=3):
        if not products:
            tk.Label(
                parent,
                text="No products found.",
                bg="#090b13",
                fg="#a6afc7",
                font=("Segoe UI", 12),
            ).grid(row=0, column=0, sticky="w", padx=6, pady=6)
            return

        for idx, product in enumerate(products):
            row, col = divmod(idx, columns)
            card = tk.Frame(parent, bg="#121b35", padx=12, pady=12, bd=0, highlightthickness=1, highlightbackground="#2d3555")
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            parent.grid_columnconfigure(col, weight=1)
            self._add_card_hover(card)

            image_label = tk.Label(card, text="Loading image...", bg="#121b35", fg="#8d97b7", width=30, height=10)
            image_label.pack(fill="x")

            fallback_path = str(self.asset_dir / product["fallback_image"])

            def update_image(photo, lbl=image_label):
                lbl.configure(image=photo, text="")
                lbl.image = photo

            self.image_loader.load(product["image_url"], fallback_path, (300, 180), update_image)

            tk.Label(
                card,
                text=product["name"],
                bg="#121b35",
                fg="#f1f4ff",
                font=("Segoe UI", 12, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(10, 0))

            tk.Label(
                card,
                text=product["description"],
                bg="#121b35",
                fg="#a8b2d0",
                font=("Segoe UI", 10),
                justify="left",
                wraplength=280,
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

            footer = tk.Frame(card, bg="#121b35")
            footer.pack(fill="x", pady=(12, 0))
            tk.Label(
                footer,
                text=f"${product['price']:.2f}",
                bg="#121b35",
                fg="#88f0cb",
                font=("Segoe UI", 12, "bold"),
            ).pack(side="left")

            add_btn = tk.Button(
                footer,
                text="Add",
                command=lambda pid=product["id"]: self.add_to_cart(pid),
                bg="#2a3e7d",
                fg="#f6f8ff",
                activebackground="#3d58ae",
                bd=0,
                padx=14,
                pady=6,
                cursor="hand2",
                font=("Segoe UI", 10, "bold"),
            )
            add_btn.pack(side="right")
            self._add_hover(add_btn, "#2a3e7d", "#3d58ae")

    def add_to_cart(self, product_id: int):
        items = {item["id"]: item for item in self.db.get_cart_items()}
        current = items.get(product_id, {}).get("quantity", 0)
        self.db.set_cart_quantity(product_id, current + 1)
        messagebox.showinfo("Added", "Item added to cart.")

    def show_cart(self):
        self._clear_content()
        self._set_active_nav("Cart")

        wrapper = self._make_scroll_frame(self.content)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)
        inner = wrapper["inner"]

        tk.Label(inner, text="Your Cart", bg="#090b13", fg="#f3f6ff", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 12))
        cart_items = self.db.get_cart_items()

        if not cart_items:
            tk.Label(inner, text="Your cart is empty.", bg="#090b13", fg="#a6afc7", font=("Segoe UI", 12)).pack(anchor="w")
            return

        for item in cart_items:
            row = tk.Frame(inner, bg="#121b35", padx=12, pady=10)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=item["name"], bg="#121b35", fg="#eef2ff", font=("Segoe UI", 11, "bold")).pack(side="left")
            tk.Label(row, text=f"${item['price']:.2f}", bg="#121b35", fg="#96eecf").pack(side="left", padx=18)

            qty_controls = tk.Frame(row, bg="#121b35")
            qty_controls.pack(side="right")

            tk.Button(qty_controls, text="-", command=lambda pid=item["id"], qty=item["quantity"]: self.update_qty(pid, qty - 1),
                      bg="#273564", fg="#fff", bd=0, width=3, cursor="hand2").pack(side="left")
            tk.Label(qty_controls, text=str(item["quantity"]), bg="#121b35", fg="#f2f6ff", width=3).pack(side="left")
            tk.Button(qty_controls, text="+", command=lambda pid=item["id"], qty=item["quantity"]: self.update_qty(pid, qty + 1),
                      bg="#273564", fg="#fff", bd=0, width=3, cursor="hand2").pack(side="left")

            tk.Label(row, text=f"Subtotal ${item['subtotal']:.2f}", bg="#121b35", fg="#ced5ea").pack(side="right", padx=18)

        total = self.db.cart_total()
        tk.Label(inner, text=f"Total: ${total:.2f}", bg="#090b13", fg="#8ef2ce", font=("Segoe UI", 14, "bold")).pack(anchor="e", pady=(12, 6))

        form = tk.Frame(inner, bg="#121b35", padx=14, pady=14)
        form.pack(fill="x", pady=10)
        tk.Label(form, text="Name", bg="#121b35", fg="#dbe3ff").grid(row=0, column=0, sticky="w")
        tk.Entry(form, textvariable=self.name_var, bg="#0f1426", fg="#f4f6ff", insertbackground="#fff", relief="flat").grid(row=1, column=0, sticky="ew", pady=(4, 10), padx=(0, 10), ipady=6)
        tk.Label(form, text="Address", bg="#121b35", fg="#dbe3ff").grid(row=0, column=1, sticky="w")
        tk.Entry(form, textvariable=self.address_var, bg="#0f1426", fg="#f4f6ff", insertbackground="#fff", relief="flat").grid(row=1, column=1, sticky="ew", pady=(4, 10), ipady=6)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        checkout_btn = tk.Button(
            inner,
            text="Place Order",
            command=self.checkout,
            bg="#3550b5",
            fg="#ffffff",
            activebackground="#4469e4",
            bd=0,
            padx=20,
            pady=10,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
        )
        checkout_btn.pack(anchor="e")
        self._add_hover(checkout_btn, "#3550b5", "#4469e4")

    def update_qty(self, product_id: int, quantity: int):
        self.db.set_cart_quantity(product_id, quantity)
        self.show_cart()

    def checkout(self):
        try:
            order_id = self.db.place_order(self.name_var.get(), self.address_var.get())
        except ValueError as exc:
            messagebox.showerror("Invalid Input", str(exc))
            return

        if order_id is None:
            messagebox.showwarning("Empty Cart", "Add items before placing an order.")
            return

        self.name_var.set("")
        self.address_var.set("")
        messagebox.showinfo("Order placed", f"Order #{order_id} has been placed successfully.")
        self.show_orders()

    def show_orders(self):
        self._clear_content()
        self._set_active_nav("Orders")

        wrapper = self._make_scroll_frame(self.content)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)
        inner = wrapper["inner"]

        tk.Label(inner, text="Order History", bg="#090b13", fg="#f3f6ff", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 12))

        orders = self.db.get_orders()
        if not orders:
            tk.Label(inner, text="No orders yet.", bg="#090b13", fg="#a6afc7", font=("Segoe UI", 12)).pack(anchor="w")
            return

        for order in orders:
            card = tk.Frame(inner, bg="#121b35", padx=14, pady=14)
            card.pack(fill="x", pady=8)
            tk.Label(card, text=f"Order #{order['id']} • ${order['total']:.2f}", bg="#121b35", fg="#ebf1ff", font=("Segoe UI", 12, "bold")).pack(anchor="w")
            tk.Label(card, text=f"{order['customer_name']} • {order['address']}", bg="#121b35", fg="#b5bfdb", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 4))
            tk.Label(card, text=f"Placed at {order['placed_at']}", bg="#121b35", fg="#9ea8c8", font=("Segoe UI", 9)).pack(anchor="w")
            for item in order["items"]:
                tk.Label(
                    card,
                    text=f"• {item['name']} x{item['quantity']} (${item['unit_price']:.2f})",
                    bg="#121b35",
                    fg="#d4dcf3",
                    font=("Segoe UI", 10),
                ).pack(anchor="w", pady=(2, 0))

    def _make_scroll_frame(self, parent):
        outer = tk.Frame(parent, bg="#090b13")
        canvas = tk.Canvas(outer, bg="#090b13", highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#090b13")

        inner.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return {"frame": outer, "canvas": canvas, "inner": inner, "pack": outer.pack}

    @staticmethod
    def _add_hover(widget: tk.Widget, base: str, hover: str):
        widget.bind("<Enter>", lambda _e: widget.configure(bg=hover))
        widget.bind("<Leave>", lambda _e: widget.configure(bg=base))

    @staticmethod
    def _add_card_hover(widget: tk.Widget):
        widget.bind("<Enter>", lambda _e: widget.configure(highlightbackground="#4b67cb"))
        widget.bind("<Leave>", lambda _e: widget.configure(highlightbackground="#2d3555"))


def run() -> None:
    app = ChickenCraveApp()
    app.mainloop()


if __name__ == "__main__":
    run()
