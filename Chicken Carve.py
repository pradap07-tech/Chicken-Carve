"""
CHICKEN CRAVE - KFC-inspired Tkinter food ordering demo.
Unofficial educational project. No affiliation with KFC.
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from pathlib import Path

BG = "#F4F4F4"
WHITE = "#FFFFFF"
DARK = "#171717"
RED = "#E4002B"
MUTED = "#777777"
BORDER = "#D8D8D8"


MENU = [
    {"name": "Double Chicken Dynamite", "category": "Double Chicken Dynamite", "price": 349, "emoji": "🍔", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60", "desc": "Two crispy chicken fillets with spicy dynamite sauce"},
    {"name": "Double Chicken Dynamite Combo", "category": "Double Chicken Dynamite", "price": 399, "emoji": "🍔🥤", "image": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&auto=format&fit=crop&q=60", "desc": "Dynamite burger with a chilled drink"},
    {"name": "Double Chicken Dynamite Meal", "category": "Double Chicken Dynamite", "price": 489, "emoji": "🍔🍟🥤", "image": "https://images.unsplash.com/photo-1610440042657-612c34d95e9f?w=500&auto=format&fit=crop&q=60", "desc": "Burger, golden fries and a refreshing drink"},
    {"name": "Double Chicken Dynamite Snack Box", "category": "Double Chicken Dynamite", "price": 499, "emoji": "🍔🍗", "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60", "desc": "Burger with crunchy chicken snacks and a drink"},
    {"name": "Double Chicken Dynamite Box Meal", "category": "Double Chicken Dynamite", "price": 569, "emoji": "🍔🍟🍗", "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60", "desc": "A loaded box meal for a bigger appetite"},

    {"name": "Wednesday Specials", "category": "Wednesday Specials", "price": 299, "emoji": "🍗🥤", "image": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500&auto=format&fit=crop&q=60", "desc": "A special chicken combo at a great price"},
    {"name": "Super Wednesday Feast", "category": "Wednesday Specials", "price": 499, "emoji": "🍗🍟🥤", "image": "https://images.unsplash.com/photo-1587314168485-3236d6710814?w=500&auto=format&fit=crop&q=60", "desc": "8 pieces of crunchy chicken tenders with spicy dips and drinks"},

    {"name": "Bucket for One", "category": "Buckets", "price": 299, "emoji": "🪣🍗", "image": "https://images.unsplash.com/photo-1513639776629-7b61b0ac49cb?w=500&auto=format&fit=crop&q=60", "desc": "A personal bucket of crispy chicken"},
    {"name": "Chicken Bucket - 6 pc", "category": "Buckets", "price": 599, "emoji": "🍗🍗", "image": "https://images.unsplash.com/photo-1569058242253-92a9c755a0ec?w=500&auto=format&fit=crop&q=60", "desc": "Six pieces of signature crispy chicken"},
    {"name": "Ultimate Family Bucket - 12 pc", "category": "Buckets", "price": 1099, "emoji": "🪣🍗🔥", "image": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=500&auto=format&fit=crop&q=60", "desc": "12 pieces of hot and crispy chicken for sharing"},
    {"name": "Smoky Grilled Chicken Bucket", "category": "Buckets", "price": 649, "emoji": "🍗🔥", "image": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=500&auto=format&fit=crop&q=60", "desc": "Slow-grilled tender chicken with bold smoky seasoning"},

    {"name": "Gold Edition Burger", "category": "Gold Edition", "price": 279, "emoji": "🍔", "image": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=500&auto=format&fit=crop&q=60", "desc": "A rich and satisfying premium burger"},
    {"name": "Gold Truffle Bacon Burger", "category": "Gold Edition", "price": 329, "emoji": "🍔🥓", "image": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=500&auto=format&fit=crop&q=60", "desc": "Crispy chicken fillet with truffle aioli and crispy smoked bacon strip"},

    {"name": "Chicken Zinger Burger", "category": "Burgers", "price": 199, "emoji": "🍔", "image": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=500&auto=format&fit=crop&q=60", "desc": "Crispy chicken, lettuce and signature sauce"},
    {"name": "Classic Veg Burger", "category": "Burgers", "price": 149, "emoji": "🥬🍔", "image": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?w=500&auto=format&fit=crop&q=60", "desc": "Crunchy veg patty with fresh lettuce"},
    {"name": "Spicy Peri-Peri Paneer Burger", "category": "Burgers", "price": 189, "emoji": "🧀🍔", "image": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=500&auto=format&fit=crop&q=60", "desc": "Thick fried cottage cheese patty tossed in fiery peri-peri spices"},
    {"name": "Tandoori Chicken Burger", "category": "Burgers", "price": 219, "emoji": "🍔🇮🇳", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60", "desc": "Grilled chicken patty infused with smoky Indian tandoori spices and mint mayo"},

    {"name": "Chicken Rice Bowl", "category": "Rice Bowlz", "price": 229, "emoji": "🍚", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60", "desc": "A hearty chicken rice bowl"},
    {"name": "Veg Fiery Rice Bowl", "category": "Rice Bowlz", "price": 189, "emoji": "🍚🥦", "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop&q=60", "desc": "Aromatic seasoned rice topped with crispy veg bites and hot garlic gravy"},

    {"name": "Classic Box Meal", "category": "Box-Meals", "price": 429, "emoji": "🍱🍗", "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60", "desc": "Chicken, fries and a drink in one box"},
    {"name": "All-Star Non-Veg Box", "category": "Box-Meals", "price": 469, "emoji": "🍱🍗🥤", "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60", "desc": "Zinger burger, 1 pc hot chicken, regular fries, and a chilled beverage"},

    {"name": "Chicken Roll", "category": "Rolls", "price": 169, "emoji": "🌯", "image": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=500&auto=format&fit=crop&q=60", "desc": "A flavour-packed chicken roll"},
    {"name": "Crispy Veggie Wrap", "category": "Rolls", "price": 139, "emoji": "🌯🥗", "image": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=500&auto=format&fit=crop&q=60", "desc": "Golden herb tortilla rolled with fresh greens, spicy potatoes, and eggless mayo"},

    {"name": "Chicken Popcorn", "category": "Snacks", "price": 179, "emoji": "🍿", "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60", "desc": "Bite-sized crispy chicken pieces"},
    {"name": "Peri Peri Fries", "category": "Snacks", "price": 119, "emoji": "🍟", "image": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=500&auto=format&fit=crop&q=60", "desc": "Golden fries with spicy seasoning"},
    {"name": "Crispy Chicken Strips (4 pc)", "category": "Snacks", "price": 169, "emoji": "🍗", "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60", "desc": "Boneless, extra crunchy hand-breaded chicken tenders"},
    {"name": "Cheesy Jalapeño Poppers", "category": "Snacks", "price": 139, "emoji": "🧀🌶️", "image": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=60", "desc": "Crispy golden bites filled with molten cheese and sliced jalapeños"},

   
    {"name": "Pepsi", "category": "Beverages & Desserts", "price": 59, "emoji": "🥤", "image": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=500&auto=format&fit=crop&q=60", "desc": "Chilled fizzy drink"},
    {"name": "Chocolate Brownie", "category": "Beverages & Desserts", "price": 99, "emoji": "🍫", "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=60", "desc": "Rich chocolate brownie"},
    {"name": "Iced Lemon Tea", "category": "Beverages & Desserts", "price": 79, "emoji": "🍋🧃", "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=500&auto=format&fit=crop&q=60", "desc": "Refreshing chilled black tea infused with real lemon pulp"},
    {"name": "Belgian Chocolate Shake", "category": "Beverages & Desserts", "price": 149, "emoji": "🥤🍫", "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=60", "desc": "Thick milkshake blended with premium dark Belgian chocolate syrup"}
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


class RoundedHeaderButton(tk.Canvas):
    """Lightweight rounded header button drawn on Canvas for a clean pill UI."""
    def __init__(self, parent, text, command, *, bg, fg, hover_bg, border=None,
                 width=160, height=46, radius=15, font=("Segoe UI", 10, "bold")):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.label_text = text
        self.command = command
        self.fill = bg
        self.text_color = fg
        self.hover_fill = hover_bg
        self.border = border
        self.radius = radius
        self.font = font
        self._draw(self.fill)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _rounded_points(self, w, h, r):
        return [r, 1, w-r, 1, w-1, r, w-1, h-r, w-r, h-1,
                r, h-1, 1, h-r, 1, r]

    def _draw(self, color):
        self.delete("all")
        w = int(self.cget("width")); h = int(self.cget("height"))
        self.create_polygon(self._rounded_points(w, h, self.radius),
                            smooth=True, splinesteps=24, fill=color,
                            outline=self.border or color, width=1)
        self.create_text(w/2, h/2, text=self.label_text, fill=self.text_color,
                         font=self.font)

    def _on_enter(self, _event):
        self._draw(self.hover_fill)

    def _on_leave(self, _event):
        self._draw(self.fill)

    def _on_click(self, _event):
        if callable(self.command):
            self.command()

    def set_text(self, text):
        self.label_text = text
        # Preserve the current hover state while refreshing the cart count.
        self._draw(self.hover_fill if self.winfo_containing(
            self.winfo_pointerx(), self.winfo_pointery()) == self else self.fill)


class ChickenCraveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CHICKEN CRAVE | Online Ordering")
        self.root.geometry("1480x940")
        self.root.minsize(980, 680)
        self.root.configure(bg="#F7F7F7")
        self.root.option_add("*Font", "{Segoe UI} 10")

        
        available_fonts = set(tkfont.families(self.root))
        self.heading_font = next(
            (name for name in ("Anton", "Impact", "Arial Black", "Arial")
             if name in available_fonts),
            "Arial"
        )
#Take me to ORDER Button


        self.cart = {}
        self.image_cache = {}  # Keeps Tkinter image objects alive.
        self.active_category = "Double Chicken Dynamite"
        self.hero_phase = 0
        self.hero_particles = []
        self.search_var = tk.StringVar()
        self.db = sqlite3.connect("chicken_crave.db")
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.initialize_database()

        self.shell = tk.Frame(root, bg=BG)
        self.shell.pack(fill="both", expand=True)
        self.build_header()
        self.page_host = tk.Frame(self.shell, bg=BG)
        self.page_host.pack(fill="both", expand=True)
        # One global wheel handler routes scrolling to whichever menu pane is under the pointer.
        self.root.bind_all("<MouseWheel>", self.route_menu_mousewheel)
        self.root.bind_all("<Button-4>", self.route_menu_mousewheel)
        self.root.bind_all("<Button-5>", self.route_menu_mousewheel)
        self.show_menu()

    # ---------------- DATABASE ----------------
    def initialize_database(self):
        with self.db:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    address TEXT NOT NULL
                )
            """)
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_code TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    total REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Placed',
                    FOREIGN KEY(customer_id) REFERENCES customers(id)
                )
            """)
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id)
                )
            """)

    # ---------------- COMMON HEADER ----------------
    def build_header(self):
        strip = tk.Frame(self.shell, bg=RED, height=30)
        strip.pack(fill="x")
        strip.pack_propagate(False)
        tk.Label(strip, text="✦  FRESHLY CRISPY. ALWAYS CRAVE-WORTHY.  ✦", bg=RED,
                 fg=WHITE, font=("Segoe UI", 9, "bold")).pack(expand=True)
        

        header = tk.Frame(self.shell, bg=WHITE, height=88,
                          highlightbackground="#EAEAEA", highlightthickness=1)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=WHITE)
        brand.pack(side="left", padx=30)
        tk.Label(brand, text="CHICKEN CRAVE", bg=WHITE, fg=RED,
                 font=(self.heading_font, 25, "bold")).pack(anchor="w", pady=(7, 0))
        tk.Label(brand, text="CRUNCH INTO HAPPINESS  •  SRMIST", bg=WHITE, fg="#555555",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")

        self.search_entry = tk.Entry(header, textvariable=self.search_var,
                                     font=(self.heading_font, 11), relief="flat",
                                     bg=BG, fg=DARK, width=30)
        self.search_entry.pack(side="left", padx=(45, 8), ipady=11)
        self.search_entry.insert(0, "Search menu...")
        self.search_entry.bind("<FocusIn>", self.clear_search_hint)
        self.search_entry.bind("<KeyRelease>", lambda _e: self.render_products())
        self.search_entry.bind("<Escape>", self.clear_search)

        self.history_button = RoundedHeaderButton(
            header, "▣  ORDER HISTORY", self.open_order_history,
            bg=WHITE, fg=RED, hover_bg="#FFF0F2", border="#F0C7D0",
            width=190, height=46, radius=16
        )
        self.history_button.pack(side="right", padx=(0, 14), pady=19)
        self.cart_button = RoundedHeaderButton(
            header, "🛒  CART (0)", self.show_checkout,
            bg=RED, fg=WHITE, hover_bg="#B90024", border=RED,
            width=156, height=46, radius=16
        )
        self.cart_button.pack(side="right", padx=(0, 14), pady=19)

    def clear_search_hint(self, _event):
        if self.search_entry.get() == "Search menu...":
            self.search_entry.delete(0, "end")

    def clear_search(self, _event=None):
        self.search_var.set("")
        self.render_products()
        return "break"

    def clear_page(self):
        for child in self.page_host.winfo_children():
            child.destroy()

    # ---------------- MENU PAGE ----------------
    def show_menu(self):
        self.clear_page()
        layout = tk.Frame(self.page_host, bg=BG)
        layout.pack(fill="both", expand=True, padx=28, pady=22)

        self.build_hero_banner(layout)

        body = tk.Frame(layout, bg=BG)
        body.pack(fill="both", expand=True)

        # Left category navigation: its own scrollable pane so every food category remains reachable.
        sidebar_wrap = tk.Frame(body, bg=WHITE, width=285,
                                highlightbackground="#CFCFCF", highlightthickness=1)
        sidebar_wrap.pack(side="left", fill="y", padx=(0, 28))
        sidebar_wrap.pack_propagate(False)
        self.sidebar_canvas = tk.Canvas(sidebar_wrap, bg=WHITE, highlightthickness=0, width=265)
        sidebar_scroll = ttk.Scrollbar(sidebar_wrap, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        sidebar_scroll.pack(side="right", fill="y")
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        self.sidebar = tk.Frame(self.sidebar_canvas, bg=WHITE)
        self.sidebar_window = self.sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")
        self.sidebar.bind("<Configure>", lambda _e: self.sidebar_canvas.configure(
            scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.bind("<Configure>", lambda e: self.sidebar_canvas.itemconfigure(
            self.sidebar_window, width=e.width))

        # Right menu cards in its own scrollable area
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.products_canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        product_scroll = ttk.Scrollbar(right, orient="vertical",
                                       command=self.products_canvas.yview)
        self.products_canvas.configure(yscrollcommand=product_scroll.set)
        product_scroll.pack(side="right", fill="y")
        self.products_canvas.pack(side="left", fill="both", expand=True)
        self.products_frame = tk.Frame(self.products_canvas, bg=BG)
        self.products_window = self.products_canvas.create_window(
            (0, 0), window=self.products_frame, anchor="nw"
        )
        self.products_frame.bind("<Configure>", self.update_products_scrollregion)
        self.products_canvas.bind(
            "<Configure>",
            lambda e: self.products_canvas.itemconfigure(self.products_window, width=e.width)
        )

        self.category_buttons = {}
        for category, emoji in CATEGORIES:
            button = tk.Button(
                self.sidebar, text=f"{emoji}    {category}",
                command=lambda c=category: self.select_category(c),
                anchor="w", bg=WHITE, fg=DARK, activebackground="#FFF0F2",
                activeforeground=RED, relief="flat", bd=0,
                font=(self.heading_font, 11), padx=18, pady=17, cursor="hand2"
            )
            button.pack(fill="x")
            tk.Frame(self.sidebar, bg="#D5D5D5", height=1).pack(fill="x")
            self.category_buttons[category] = button

        self.render_products()

    def build_hero_banner(self, parent):
        """Animated promotional banner drawn with native Tkinter Canvas."""
        self.hero = tk.Canvas(parent, height=158, bg="#241012", highlightthickness=0)
        self.hero.pack(fill="x", pady=(0, 18))
        self.hero.bind("<Configure>", self.draw_hero)
        self.draw_hero()
        self.animate_hero()

    def draw_hero(self, _event=None):
        if not hasattr(self, "hero") or not self.hero.winfo_exists():
            return
        c = self.hero
        c.delete("all")
        w = max(c.winfo_width(), 500)
        h = max(c.winfo_height(), 158)
        # Rich red layered backdrop with angled panels.
        c.create_rectangle(0, 0, w, h, fill="#8E001C", outline="")
        c.create_polygon(w*.55, 0, w, 0, w, h, w*.72, h, fill="#B90024", outline="")
        c.create_oval(w-210, -100, w+30, 140, fill="#D51A38", outline="")
        c.create_oval(w-145, 40, w+25, 210, fill="#A80021", outline="")
        c.create_text(34, 17, text="THE CRUNCH CLUB", anchor="w", fill="#FFD9A8",
                      font=("Segoe UI", 9, "bold"))
        c.create_text(32, 82, text="BIG FLAVOUR.\nBIGGER CRAVINGS.", anchor="w",
                      fill=WHITE, font=(self.heading_font, 23, "bold"), justify="left")
        c.create_text(35, 137, text="Your favourites are just a few clicks away.",
                      anchor="w", fill="#FFE9E9", font=("Segoe UI", 10))
        c.create_text(w-115, 76, text="🍗", fill=WHITE, font=("Segoe UI Emoji", 66))
        c.create_text(w-265, 35, text="✦  HOT & CRISPY  ✦", fill="#FFE3B4",
                      font=("Segoe UI", 9, "bold"))
        self.hero_particles = []
        for i in range(12):
            x = w - 300 + (i * 31) % 280
            y = 15 + (i * 23) % 125
            dot = c.create_oval(x, y, x+4, y+4, fill="#FFD7A0", outline="")
            self.hero_particles.append((dot, x, y, i))

    def animate_hero(self):
        if not hasattr(self, "hero") or not self.hero.winfo_exists():
            return
        self.hero_phase += 1
        for dot, x, y, seed in self.hero_particles:
            drift = (self.hero_phase + seed * 7) % 34
            try:
                self.hero.coords(dot, x, y - drift/3, x+4, y+4 - drift/3)
            except tk.TclError:
                pass
        self.hero.after(75, self.animate_hero)

    def update_products_scrollregion(self, _event=None):
        self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all"))

    def route_menu_mousewheel(self, event):
        """Scroll the menu pane currently under the mouse, including its child widgets."""
        try:
            hovered = self.root.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            return
        target = None
        widget = hovered
        while widget is not None:
            if widget == getattr(self, "products_canvas", None):
                target = self.products_canvas
                break
            if widget == getattr(self, "sidebar_canvas", None):
                target = self.sidebar_canvas
                break
            widget = getattr(widget, "master", None)
        if target is None:
            return
        if getattr(event, "num", None) == 4:
            units = -3
        elif getattr(event, "num", None) == 5:
            units = 3
        else:
            delta = event.delta
            units = -int(delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
        target.yview_scroll(units, "units")
        return "break"

    def select_category(self, category):
        self.active_category = category
        self.search_var.set("")
        for name, button in self.category_buttons.items():
            button.configure(
                bg="#FFF0F2" if name == category else WHITE,
                fg=RED if name == category else DARK,
                font=(self.heading_font, 11, "bold" if name == category else "normal")
            )
        self.render_products()

    def render_products(self):
        if not hasattr(self, "products_frame") or not self.products_frame.winfo_exists():
            return
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        self.products_canvas.yview_moveto(0)
        self.products_canvas.after_idle(self.update_products_scrollregion)

        query = self.search_var.get().strip().lower()
        if query == "search menu...":
            query = ""
        products = [
            item for item in MENU
            if (query or item["category"] == self.active_category)
            and (not query or query in item["name"].lower()
                 or query in item["desc"].lower()
                 or query in item["category"].lower())
        ]

        if not products:
            tk.Label(self.products_frame, text="No items found in this category.",
                     bg=BG, fg=MUTED, font=(self.heading_font, 13)).pack(pady=40)
            return

        for col in range(3):
            self.products_frame.grid_columnconfigure(col, weight=1, uniform="product")
        for index, item in enumerate(products):
            row, col = divmod(index, 3)
            self.product_card(self.products_frame, item, row, col)

        for name, button in self.category_buttons.items():
            button.configure(
                bg="#FFF0F2" if name == self.active_category else WHITE,
                fg=RED if name == self.active_category else DARK,
                font=(self.heading_font, 11, "bold" if name == self.active_category else "normal")
            )

    def load_product_image(self, item, max_size=(220, 205)):
        """Load a product picture from its image path; return None if not configured."""
        image_path = item.get("image", "").strip()
        if not image_path:
            return None

        base_dir = Path(__file__).resolve().parent
        if image_path.startswith(("https://", "http://")):
            # Download online menu photos once, then reuse the local cache.
            import hashlib
            import urllib.request
            cache_dir = base_dir / "product_images"
            cache_dir.mkdir(exist_ok=True)
            suffix = Path(image_path.split("?", 1)[0]).suffix or ".jpg"
            filename = hashlib.md5(image_path.encode("utf-8")).hexdigest() + suffix
            full_path = cache_dir / filename
            if not full_path.exists():
                try:
                    request = urllib.request.Request(
                        image_path, headers={"User-Agent": "ChickenCrave/1.0"}
                    )
                    with urllib.request.urlopen(request, timeout=1.5) as response:
                        full_path.write_bytes(response.read())
                except Exception:
                    return None
        else:
            full_path = base_dir / image_path
        if not full_path.is_file():
            return None

        cache_key = (str(full_path), max_size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        # Pillow enables automatic resizing and JPG/JPEG/WEBP support.
        try:
            from PIL import Image, ImageTk
            with Image.open(full_path) as source:
                source = source.convert("RGBA")
                source.thumbnail(max_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(source)
        except ImportError:
            # Without Pillow, Tkinter can directly load PNG and GIF files.
            try:
                photo = tk.PhotoImage(file=str(full_path))
                factor = max(
                    1,
                    (photo.width() + max_size[0] - 1) // max_size[0],
                    (photo.height() + max_size[1] - 1) // max_size[1]
                )
                if factor > 1:
                    photo = photo.subsample(factor, factor)
            except tk.TclError:
                return None
        except Exception:
            return None

        self.image_cache[cache_key] = photo
        return photo

    @staticmethod
    def rounded_rect(canvas, x1, y1, x2, y2, radius=18, **kwargs):
        """Draw a smooth rounded rectangle using a polygon with curved joints."""
        radius = max(2, min(radius, (x2-x1)/2, (y2-y1)/2))
        points = [x1+radius,y1, x2-radius,y1, x2-radius/2,y1,
                  x2,y1+radius/2, x2,y2-radius, x2,y2-radius/2,
                  x2-radius/2,y2, x1+radius,y2, x1+radius/2,y2,
                  x1,y2-radius/2, x1,y1+radius, x1,y1+radius/2]
        return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

    def animated_button(self, parent, text, command, width=156, height=42):
        """Canvas button with rounded corners and a short, lightweight hover fade."""
        widget = tk.Canvas(parent, width=width, height=height, bg=WHITE,
                           highlightthickness=0, bd=0, cursor="hand2")
        widget._button_bg = RED
        widget._target_bg = RED
        widget._button_text = text
        widget._command = command
        widget._shape = self.rounded_rect(widget, 2, 2, width-2, height-2,
                                          radius=14, fill=RED, outline=RED)
        widget._label = widget.create_text(width/2, height/2, text=text,
                                           fill=WHITE, font=("Segoe UI", 9, "bold"))
        def hover(_event, color):
            widget._target_bg = color
            if getattr(widget, "_animating", False):
                return
            widget._animating = True
            start_color = widget._button_bg
            target_color = color
            def rgb(value):
                value = value.lstrip("#")
                return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
            start_rgb, target_rgb = rgb(start_color), rgb(target_color)
            def frame(step=1):
                if not widget.winfo_exists():
                    return
                ratio = step / 6
                mixed = tuple(round(a + (b-a)*ratio) for a, b in zip(start_rgb, target_rgb))
                shade = "#" + "".join(f"{v:02x}" for v in mixed)
                widget._button_bg = shade
                widget.itemconfigure(widget._shape, fill=shade, outline=shade)
                if step < 6:
                    widget.after(16, lambda: frame(step+1))
                else:
                    widget._animating = False
                    if widget._target_bg != target_color:
                        hover(None, widget._target_bg)
            widget.after(1, frame)
        widget.bind("<Enter>", lambda e: hover(e, "#B90024"))
        widget.bind("<Leave>", lambda e: hover(e, RED))
        widget.bind("<Button-1>", lambda _e: command())
        return widget

    def product_card(self, parent, item, row, col):
        # Rounded canvas shell creates the card silhouette; inset content keeps corners visible.
        shell = tk.Canvas(parent, bg=BG, highlightthickness=0, bd=0, height=414)
        shell.grid(row=row, column=col, sticky="nsew", padx=9, pady=9)
        shell.grid_propagate(False)
        shell.configure(height=414)
        shell.bind("<Configure>", lambda e, c=shell: self._draw_card_surface(c, e.width, e.height, False))
        content = tk.Frame(shell, bg=WHITE, bd=0)
        window = shell.create_window(5, 5, anchor="nw", window=content)
        def resize_content(event, c=shell, w=window):
            c.itemconfigure(w, width=max(1, event.width-10), height=max(1, event.height-10))
            self._draw_card_surface(c, event.width, event.height, False)
        shell.bind("<Configure>", resize_content)
        shell.bind("<Enter>", lambda _e, c=shell: self._draw_card_surface(c, c.winfo_width(), c.winfo_height(), True))
        shell.bind("<Leave>", lambda _e, c=shell: self._draw_card_surface(c, c.winfo_width(), c.winfo_height(), False))

        image_area = tk.Frame(content, bg="#FFF7F4", height=194)
        image_area.pack(fill="x", padx=9, pady=(9, 0))
        image_area.pack_propagate(False)
        product_image = self.load_product_image(item, max_size=(240, 185))
        if product_image is not None:
            image_label = tk.Label(image_area, image=product_image, bg="#FFF7F4")
            image_label.image = product_image
            image_label.pack(expand=True)
        else:
            tk.Label(image_area, text=item["emoji"], bg="#FFF7F4",
                     font=("Segoe UI Emoji", 58)).pack(expand=True)

        tk.Label(content, text=item["name"].upper(), bg=WHITE, fg=DARK,
                 font=(self.heading_font, 12, "bold"), justify="left",
                 anchor="w", wraplength=235, height=2).pack(
                     fill="x", padx=14, pady=(9, 2))
        tk.Label(content, text=item["desc"], bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9), justify="left", anchor="w",
                 wraplength=235, height=2).pack(fill="x", padx=14)
        bottom = tk.Frame(content, bg=WHITE)
        bottom.pack(fill="x", padx=14, pady=(9, 12))
        tk.Label(bottom, text=f"₹ {item['price']:.2f}", bg=WHITE, fg="#171717",
                 font=(self.heading_font, 16, "bold")).pack(side="left")
        self.animated_button(bottom, "ADD TO CART  +", lambda p=item: self.order_now(p),
                             width=140, height=39).pack(side="right")

    def _draw_card_surface(self, canvas, width, height, hovered):
        if not canvas.winfo_exists() or width < 20 or height < 20:
            return
        canvas.delete("surface")
        color = "#FFD2DA" if hovered else "#E7E4E4"
        self.rounded_rect(canvas, 1, 1, width-2, height-2, radius=20,
                          fill=WHITE, outline=color, width=2 if hovered else 1,
                          tags="surface")
        canvas.tag_lower("surface")

    def order_now(self, item):
        self.add_to_cart(item)
        # Stay on the menu; checkout opens only when the customer presses CART.
        self.show_add_feedback(item)

    def show_add_feedback(self, item):
        """Brief, non-blocking confirmation without navigating away from the menu."""
        if not hasattr(self, "page_host") or not self.page_host.winfo_exists():
            return
        if hasattr(self, "add_feedback") and self.add_feedback.winfo_exists():
            self.add_feedback.destroy()
        self.add_feedback = tk.Label(
            self.shell, text=f"✓  {item['name']} added to cart", bg="#202020", fg=WHITE,
            font=("Segoe UI", 10, "bold"), padx=18, pady=10
        )
        self.add_feedback.place(relx=0.98, rely=0.98, anchor="se")
        self.add_feedback.after(1600, lambda: self.add_feedback.destroy()
                                if self.add_feedback.winfo_exists() else None)

    # ---------------- CART + CHECKOUT PAGE ----------------
    def add_to_cart(self, item):
        name = item["name"]
        if name in self.cart:
            self.cart[name]["qty"] += 1
        else:
            self.cart[name] = {**item, "qty": 1}
        self.update_cart_button()

    def update_cart_button(self):
        count = sum(item["qty"] for item in self.cart.values())
        self.cart_button.set_text(f"🛒  CART ({count})")

    def cart_total(self):
        return sum(item["price"] * item["qty"] for item in self.cart.values())

    def show_checkout(self):
        self.clear_page()
        page = tk.Frame(self.page_host, bg=BG)
        page.pack(fill="both", expand=True, padx=45, pady=26)

        nav = tk.Frame(page, bg=BG)
        nav.pack(fill="x", pady=(0, 20))
        tk.Button(nav, text="← BACK TO MENU", command=self.show_menu,
                  bg=WHITE, fg=RED, relief="flat", font=("Arial", 10, "bold"),
                  padx=15, pady=9, cursor="hand2").pack(side="left")
        tk.Label(nav, text="CHECKOUT", bg=BG, fg=DARK,
                 font=(self.heading_font, 27, "bold")).pack(side="right")

        if not self.cart:
            tk.Label(page, text="Your cart is empty 🍗", bg=BG, fg=MUTED,
                     font=("Arial", 17, "bold")).pack(pady=70)
            tk.Button(page, text="EXPLORE MENU", command=self.show_menu,
                      bg=RED, fg=WHITE, relief="flat", padx=20, pady=12).pack()
            return

        columns = tk.Frame(page, bg=BG)
        columns.pack(fill="both", expand=True)
        summary = tk.Frame(columns, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        summary.pack(side="left", fill="both", expand=True, padx=(0, 18))
        details = tk.Frame(columns, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        details.pack(side="left", fill="y", ipadx=10)

        tk.Label(summary, text="YOUR ORDER  🍗", bg=WHITE, fg=DARK,
                 font=(self.heading_font, 19, "bold")).pack(anchor="w", padx=22, pady=(20, 12))
        self.checkout_items = tk.Frame(summary, bg=WHITE)
        self.checkout_items.pack(fill="x", padx=22)
        self.checkout_total = tk.Label(summary, text="", bg=WHITE, fg=RED,
                                       font=("Arial", 17, "bold"))
        self.checkout_total.pack(anchor="e", padx=22, pady=20)
        self.render_checkout_items()

        tk.Label(details, text="DELIVERY DETAILS", bg=WHITE, fg=RED,
                 font=(self.heading_font, 18, "bold")).pack(anchor="w", padx=22, pady=(20, 5))
        tk.Label(details, text="Where should we bring your food?",
                 bg=WHITE, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=22, pady=(0, 10))
        self.name_entry = self.form_entry(details, "Full name")
        self.phone_entry = self.form_entry(details, "10-digit mobile number")
        self.address_entry = self.form_entry(details, "Delivery address", multiline=True)
        tk.Label(details, text="PAYMENT METHOD", bg=WHITE, fg=DARK,
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=22, pady=(12, 5))
        self.payment_var = tk.StringVar(value="Cash on Delivery")
        ttk.Combobox(details, textvariable=self.payment_var,
                     values=["Cash on Delivery", "UPI (demo only)"],
                     state="readonly", width=28).pack(anchor="w", padx=22, ipady=5)
        tk.Button(details, text="PLACE DEMO ORDER  →", command=self.submit_order,
                  bg=RED, fg=WHITE, activebackground="#B90024",
                  activeforeground=WHITE, relief="flat",
                  font=("Arial", 10, "bold"), padx=15, pady=13,
                  cursor="hand2").pack(fill="x", padx=22, pady=24)

    def form_entry(self, parent, label, multiline=False):
        tk.Label(parent, text=label, bg=WHITE, fg=DARK,
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=22, pady=(9, 4))
        if multiline:
            widget = tk.Text(parent, height=4, width=31, font=("Arial", 10),
                             relief="solid", bd=1, wrap="word")
        else:
            widget = tk.Entry(parent, width=34, font=("Arial", 10),
                              relief="solid", bd=1)
        widget.pack(anchor="w", padx=22, ipady=7 if not multiline else 2)
        return widget

    def render_checkout_items(self):
        for child in self.checkout_items.winfo_children():
            child.destroy()
        for name, item in self.cart.items():
            row = tk.Frame(self.checkout_items, bg=WHITE)
            row.pack(fill="x", pady=8)
            tk.Label(row, text=f"{item['emoji']}  {name}",
                     bg=WHITE, fg=DARK, font=("Arial", 10, "bold"),
                     wraplength=260, justify="left").pack(side="left")
            tk.Label(row, text=f"₹{item['price'] * item['qty']}",
                     bg=WHITE, fg=DARK, font=("Arial", 10, "bold")).pack(side="right")
            controls = tk.Frame(self.checkout_items, bg=WHITE)
            controls.pack(anchor="w", pady=(0, 5))
            tk.Button(controls, text="−", width=3,
                      command=lambda n=name: self.checkout_change_qty(n, -1)).pack(side="left")
            tk.Label(controls, text=f"  {item['qty']}  ", bg=WHITE,
                     font=("Arial", 9, "bold")).pack(side="left")
            tk.Button(controls, text="+", width=3,
                      command=lambda n=name: self.checkout_change_qty(n, 1)).pack(side="left")
        self.checkout_total.configure(text=f"TOTAL: ₹{self.cart_total():.2f}")

    def checkout_change_qty(self, name, delta):
        self.cart[name]["qty"] += delta
        if self.cart[name]["qty"] <= 0:
            del self.cart[name]
        self.update_cart_button()
        self.show_checkout()

    def submit_order(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get("1.0", "end").strip()
        if not name or not phone or not address:
            messagebox.showwarning("Missing details", "Please fill in all delivery details.")
            return
        if not phone.isdigit() or len(phone) != 10:
            messagebox.showwarning("Invalid mobile number", "Enter a valid 10-digit mobile number.")
            return

        total = self.cart_total()
        order_code = "CC" + datetime.now().strftime("%y%m%d%H%M%S%f")
        order_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        payment = self.payment_var.get()

        try:
            with self.db:
                existing = self.db.execute(
                    "SELECT id FROM customers WHERE phone = ?", (phone,)
                ).fetchone()
                if existing:
                    customer_id = existing["id"]
                    self.db.execute(
                        "UPDATE customers SET name=?, address=? WHERE id=?",
                        (name, address, customer_id)
                    )
                else:
                    cursor = self.db.execute(
                        "INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)",
                        (name, phone, address)
                    )
                    customer_id = cursor.lastrowid

                cursor = self.db.execute("""
                    INSERT INTO orders
                    (order_code, customer_id, order_date, total, payment_method, status)
                    VALUES (?, ?, ?, ?, ?, 'Placed')
                """, (order_code, customer_id, order_date, total, payment))
                order_id = cursor.lastrowid
                self.db.executemany("""
                    INSERT INTO order_items (order_id, product_name, quantity, unit_price)
                    VALUES (?, ?, ?, ?)
                """, [
                    (order_id, item["name"], item["qty"], item["price"])
                    for item in self.cart.values()
                ])
        except sqlite3.Error as exc:
            messagebox.showerror("Database error", f"Could not save your order:\n{exc}")
            return

        messagebox.showinfo(
            "Order placed!",
            f"Thank you, {name}! 🍗\n\nOrder ID: {order_code}\n"
            f"Total: ₹{total:.2f}\n\nYour demo order has been saved."
        )
        self.cart.clear()
        self.update_cart_button()
        self.show_menu()

    # ---------------- ORDER HISTORY ----------------
    def open_order_history(self):
        win = tk.Toplevel(self.root)
        win.title("Order History")
        win.geometry("800x520")
        win.configure(bg=WHITE)
        win.transient(self.root)

        tk.Label(win, text="YOUR PREVIOUS ORDERS", bg=WHITE, fg=RED,
                 font=("Arial", 19, "bold")).pack(anchor="w", padx=22, pady=(20, 5))
        tk.Label(win, text="Search using the mobile number entered at checkout.",
                 bg=WHITE, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=22)

        search = tk.Frame(win, bg=WHITE)
        search.pack(fill="x", padx=22, pady=15)
        phone = tk.Entry(search, font=("Arial", 11), relief="solid", bd=1)
        phone.pack(side="left", fill="x", expand=True, ipady=8)
        results = tk.Frame(win, bg=WHITE)
        results.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        def search_history():
            number = phone.get().strip()
            if not number.isdigit() or len(number) != 10:
                messagebox.showwarning("Invalid number", "Enter a valid 10-digit mobile number.", parent=win)
                return
            for child in results.winfo_children():
                child.destroy()
            rows = self.db.execute("""
                SELECT o.id, o.order_code, o.order_date, o.total, o.payment_method, o.status
                FROM orders o JOIN customers c ON c.id=o.customer_id
                WHERE c.phone=? ORDER BY o.id DESC
            """, (number,)).fetchall()
            if not rows:
                tk.Label(results, text="No previous orders found.",
                         bg=WHITE, fg=MUTED, font=("Arial", 11)).pack(pady=25)
                return
            table = ttk.Treeview(results,
                columns=("code", "date", "total", "payment", "status"),
                show="headings", height=10)
            for col, title, width in [
                ("code", "Order ID", 190), ("date", "Date", 150),
                ("total", "Total", 100), ("payment", "Payment", 140),
                ("status", "Status", 100)
            ]:
                table.heading(col, text=title)
                table.column(col, width=width, anchor="center")
            table.pack(fill="both", expand=True)
            for row in rows:
                table.insert("", "end", iid=str(row["id"]), values=(
                    row["order_code"], row["order_date"], f"₹{row['total']:.2f}",
                    row["payment_method"], row["status"]
                ))

            def show_items(_event=None):
                selected = table.selection()
                if not selected:
                    return
                items = self.db.execute("""
                    SELECT product_name, quantity, unit_price
                    FROM order_items WHERE order_id=?
                """, (int(selected[0]),)).fetchall()
                details = "\n".join(
                    f"{i['product_name']} × {i['quantity']} = ₹{i['quantity'] * i['unit_price']:.2f}"
                    for i in items
                )
                messagebox.showinfo("Order items", details or "No items found.", parent=win)
            table.bind("<<TreeviewSelect>>", show_items)

        tk.Button(search, text="SEARCH", command=search_history,
                  bg=RED, fg=WHITE, relief="flat", padx=18, pady=9,
                  font=("Arial", 9, "bold")).pack(side="left", padx=(8, 0))


if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = ChickenCraveApp(root)
    except Exception as exc:
        messagebox.showerror("Chicken Crave startup error", str(exc))
        root.destroy()
        raise

    def close_app():
        try:
            app.db.close()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()
