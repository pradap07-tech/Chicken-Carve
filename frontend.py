import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
from typing import Optional, Callable

from backend import BackendService

BG = "#F4F4F4"
WHITE = "#FFFFFF"
DARK = "#171717"
RED = "#E4002B"
MUTED = "#777777"
BORDER = "#D8D8D8"


class RoundedHeaderButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text: str,
        command: Optional[Callable[[], None]] = None,
        *,
        bg: str = WHITE,
        fg: str = DARK,
        hover_bg: str = "#FFF0F2",
        border: Optional[str] = None,
        width: int = 160,
        height: int = 46,
        radius: int = 15,
        font: tuple = ("Segoe UI", 10, "bold")
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )
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

    def _rounded_points(self, w: int, h: int, r: int):
        return [
            r, 1, w - r, 1, w - 1, r, w - 1, h - r, w - r, h - 1,
            r, h - 1, 1, h - r, 1, r
        ]

    def _draw(self, color: str):
        self.delete("all")
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        self.create_polygon(
            self._rounded_points(w, h, self.radius),
            smooth=True,
            splinesteps=24,
            fill=color,
            outline=self.border or color,
            width=1
        )
        self.create_text(
            w / 2,
            h / 2,
            text=self.label_text,
            fill=self.text_color,
            font=self.font
        )

    def _on_enter(self, _event):
        self._draw(self.hover_fill)

    def _on_leave(self, _event):
        self._draw(self.fill)

    def _on_click(self, _event):
        if callable(self.command):
            self.command()

    def set_text(self, text: str):
        self.label_text = text
        try:
            under_pointer = (
                self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery()) == self
            )
            self._draw(self.hover_fill if under_pointer else self.fill)
        except Exception:
            self._draw(self.fill)


class ChickenCraveApp:
    def __init__(self, root: tk.Tk, backend: BackendService):
        self.root = root
        self.backend = backend

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

        categories = self.backend.get_categories()
        self.active_category = categories[0][0] if categories else ""
        self.hero_phase = 0
        self.hero_particles = []
        self.search_var = tk.StringVar()

        self.shell = tk.Frame(root, bg=BG)
        self.shell.pack(fill="both", expand=True)

        self.build_header()
        self.page_host = tk.Frame(self.shell, bg=BG)
        self.page_host.pack(fill="both", expand=True)

        self.root.bind_all("<MouseWheel>", self.route_menu_mousewheel)
        self.root.bind_all("<Button-4>", self.route_menu_mousewheel)
        self.root.bind_all("<Button-5>", self.route_menu_mousewheel)

        self.show_menu()

    def build_header(self):
        strip = tk.Frame(self.shell, bg=RED, height=30)
        strip.pack(fill="x")
        strip.pack_propagate(False)
        tk.Label(
            strip,
            text="✦  FRESHLY CRISPY. ALWAYS CRAVE-WORTHY.  ✦",
            bg=RED,
            fg=WHITE,
            font=("Segoe UI", 9, "bold")
        ).pack(expand=True)

        header = tk.Frame(
            self.shell,
            bg=WHITE,
            height=88,
            highlightbackground="#EAEAEA",
            highlightthickness=1
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=WHITE)
        brand.pack(side="left", padx=30)
        tk.Label(
            brand,
            text="CHICKEN CRAVE",
            bg=WHITE,
            fg=RED,
            font=(self.heading_font, 25, "bold")
        ).pack(anchor="w", pady=(7, 0))
        tk.Label(
            brand,
            text="CRUNCH INTO HAPPINESS  •  SRMIST",
            bg=WHITE,
            fg="#555555",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        self.search_entry = tk.Entry(
            header,
            textvariable=self.search_var,
            font=(self.heading_font, 11),
            relief="flat",
            bg=BG,
            fg=DARK,
            width=30
        )
        self.search_entry.pack(side="left", padx=(45, 8), ipady=11)
        self.search_entry.insert(0, "Search menu...")
        self.search_entry.bind("<FocusIn>", self.clear_search_hint)
        self.search_entry.bind("<KeyRelease>", lambda _e: self.render_products())
        self.search_entry.bind("<Escape>", self.clear_search)

        self.history_button = RoundedHeaderButton(
            header,
            "▣  ORDER HISTORY",
            self.open_order_history,
            bg=WHITE,
            fg=RED,
            hover_bg="#FFF0F2",
            border="#F0C7D0",
            width=190,
            height=46,
            radius=16
        )
        self.history_button.pack(side="right", padx=(0, 14), pady=19)

        self.cart_button = RoundedHeaderButton(
            header,
            "🛒  CART (0)",
            self.show_checkout,
            bg=RED,
            fg=WHITE,
            hover_bg="#B90024",
            border=RED,
            width=156,
            height=46,
            radius=16
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

    def update_cart_button(self):
        count = self.backend.cart.get_count()
        self.cart_button.set_text(f"🛒  CART ({count})")

    def show_menu(self):
        self.clear_page()
        layout = tk.Frame(self.page_host, bg=BG)
        layout.pack(fill="both", expand=True, padx=28, pady=22)

        self.build_hero_banner(layout)

        body = tk.Frame(layout, bg=BG)
        body.pack(fill="both", expand=True)

        sidebar_wrap = tk.Frame(
            body,
            bg=WHITE,
            width=285,
            highlightbackground="#CFCFCF",
            highlightthickness=1
        )
        sidebar_wrap.pack(side="left", fill="y", padx=(0, 28))
        sidebar_wrap.pack_propagate(False)

        self.sidebar_canvas = tk.Canvas(sidebar_wrap, bg=WHITE, highlightthickness=0, width=265)
        sidebar_scroll = ttk.Scrollbar(sidebar_wrap, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        sidebar_scroll.pack(side="right", fill="y")
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)

        self.sidebar = tk.Frame(self.sidebar_canvas, bg=WHITE)
        self.sidebar_window = self.sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")
        self.sidebar.bind(
            "<Configure>",
            lambda _e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
        )
        self.sidebar_canvas.bind(
            "<Configure>",
            lambda e: self.sidebar_canvas.itemconfigure(self.sidebar_window, width=e.width)
        )

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.products_canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        product_scroll = ttk.Scrollbar(right, orient="vertical", command=self.products_canvas.yview)
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
        for category, emoji in self.backend.get_categories():
            button = tk.Button(
                self.sidebar,
                text=f"{emoji}    {category}",
                command=lambda c=category: self.select_category(c),
                anchor="w",
                bg=WHITE,
                fg=DARK,
                activebackground="#FFF0F2",
                activeforeground=RED,
                relief="flat",
                bd=0,
                font=(self.heading_font, 11),
                padx=18,
                pady=17,
                cursor="hand2"
            )
            button.pack(fill="x")
            tk.Frame(self.sidebar, bg="#D5D5D5", height=1).pack(fill="x")
            self.category_buttons[category] = button

        self.render_products()

    def build_hero_banner(self, parent):
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

        c.create_rectangle(0, 0, w, h, fill="#8E001C", outline="")
        c.create_polygon(w * 0.55, 0, w, 0, w, h, w * 0.72, h, fill="#B90024", outline="")
        c.create_oval(w - 210, -100, w + 30, 140, fill="#D51A38", outline="")
        c.create_oval(w - 145, 40, w + 25, 210, fill="#A80021", outline="")
        c.create_text(
            34, 17, text="THE CRUNCH CLUB", anchor="w", fill="#FFD9A8", font=("Segoe UI", 9, "bold")
        )
        c.create_text(
            32, 82, text="BIG FLAVOUR.\nBIGGER CRAVINGS.", anchor="w",
            fill=WHITE, font=(self.heading_font, 23, "bold"), justify="left"
        )
        c.create_text(
            35, 137, text="Your favourites are just a few clicks away.",
            anchor="w", fill="#FFE9E9", font=("Segoe UI", 10)
        )
        c.create_text(w - 115, 76, text="🍗", fill=WHITE, font=("Segoe UI Emoji", 66))
        c.create_text(w - 265, 35, text="✦  HOT & CRISPY  ✦", fill="#FFE3B4", font=("Segoe UI", 9, "bold"))

        self.hero_particles = []
        for i in range(12):
            x = w - 300 + (i * 31) % 280
            y = 15 + (i * 23) % 125
            dot = c.create_oval(x, y, x + 4, y + 4, fill="#FFD7A0", outline="")
            self.hero_particles.append((dot, x, y, i))

    def animate_hero(self):
        if not hasattr(self, "hero") or not self.hero.winfo_exists():
            return
        self.hero_phase += 1
        for dot, x, y, seed in self.hero_particles:
            drift = (self.hero_phase + seed * 7) % 34
            try:
                self.hero.coords(dot, x, y - drift / 3, x + 4, y + 4 - drift / 3)
            except tk.TclError:
                pass
        self.hero.after(75, self.animate_hero)

    def update_products_scrollregion(self, _event=None):
        if hasattr(self, "products_canvas") and self.products_canvas.winfo_exists():
            self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all"))

    def route_menu_mousewheel(self, event):
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

    def select_category(self, category: str):
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

        products = self.backend.get_filtered_menu(
            active_category=self.active_category,
            query=self.search_var.get()
        )

        if not products:
            tk.Label(
                self.products_frame,
                text="No items found in this category.",
                bg=BG,
                fg=MUTED,
                font=(self.heading_font, 13)
            ).pack(pady=40)
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

    @staticmethod
    def rounded_rect(canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float, radius: int = 18, **kwargs):
        radius = max(2, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
        points = [
            x1 + radius, y1, x2 - radius, y1, x2 - radius / 2, y1,
            x2, y1 + radius / 2, x2, y2 - radius, x2, y2 - radius / 2,
            x2 - radius / 2, y2, x1 + radius, y2, x1 + radius / 2, y2,
            x1, y2 - radius / 2, x1, y1 + radius, x1, y1 + radius / 2
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

    def animated_button(self, parent, text: str, command: Callable[[], None], width: int = 156, height: int = 42):
        widget = tk.Canvas(parent, width=width, height=height, bg=WHITE, highlightthickness=0, bd=0, cursor="hand2")
        widget._button_bg = RED
        widget._target_bg = RED
        widget._button_text = text
        widget._command = command
        widget._shape = self.rounded_rect(widget, 2, 2, width - 2, height - 2, radius=14, fill=RED, outline=RED)
        widget._label = widget.create_text(width / 2, height / 2, text=text, fill=WHITE, font=("Segoe UI", 9, "bold"))

        def hover(_event, color):
            widget._target_bg = color
            if getattr(widget, "_animating", False):
                return
            widget._animating = True
            start_color = widget._button_bg
            target_color = color

            def rgb(value):
                value = value.lstrip("#")
                return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

            start_rgb, target_rgb = rgb(start_color), rgb(target_color)

            def frame(step=1):
                if not widget.winfo_exists():
                    return
                ratio = step / 6
                mixed = tuple(round(a + (b - a) * ratio) for a, b in zip(start_rgb, target_rgb))
                shade = "#" + "".join(f"{v:02x}" for v in mixed)
                widget._button_bg = shade
                widget.itemconfigure(widget._shape, fill=shade, outline=shade)
                if step < 6:
                    widget.after(16, lambda: frame(step + 1))
                else:
                    widget._animating = False
                    if widget._target_bg != target_color:
                        hover(None, widget._target_bg)

            widget.after(1, frame)

        widget.bind("<Enter>", lambda e: hover(e, "#B90024"))
        widget.bind("<Leave>", lambda e: hover(e, RED))
        widget.bind("<Button-1>", lambda _e: command())
        return widget

    def product_card(self, parent, item: dict, row: int, col: int):
        shell = tk.Canvas(parent, bg=BG, highlightthickness=0, bd=0, height=414)
        shell.grid(row=row, column=col, sticky="nsew", padx=9, pady=9)
        shell.grid_propagate(False)
        shell.configure(height=414)
        shell.bind("<Configure>", lambda e, c=shell: self._draw_card_surface(c, e.width, e.height, False))

        content = tk.Frame(shell, bg=WHITE, bd=0)
        window = shell.create_window(5, 5, anchor="nw", window=content)

        def resize_content(event, c=shell, w=window):
            c.itemconfigure(w, width=max(1, event.width - 10), height=max(1, event.height - 10))
            self._draw_card_surface(c, event.width, event.height, False)

        shell.bind("<Configure>", resize_content)
        shell.bind("<Enter>", lambda _e, c=shell: self._draw_card_surface(c, c.winfo_width(), c.winfo_height(), True))
        shell.bind("<Leave>", lambda _e, c=shell: self._draw_card_surface(c, c.winfo_width(), c.winfo_height(), False))

        image_area = tk.Frame(content, bg="#FFF7F4", height=194)
        image_area.pack(fill="x", padx=9, pady=(9, 0))
        image_area.pack_propagate(False)

        product_image = self.backend.images.get_image(item, max_size=(240, 185))
        if product_image is not None:
            image_label = tk.Label(image_area, image=product_image, bg="#FFF7F4")
            image_label.image = product_image
            image_label.pack(expand=True)
        else:
            tk.Label(image_area, text=item["emoji"], bg="#FFF7F4", font=("Segoe UI Emoji", 58)).pack(expand=True)

        tk.Label(
            content,
            text=item["name"].upper(),
            bg=WHITE,
            fg=DARK,
            font=(self.heading_font, 12, "bold"),
            justify="left",
            anchor="w",
            wraplength=235,
            height=2
        ).pack(fill="x", padx=14, pady=(9, 2))

        tk.Label(
            content,
            text=item["desc"],
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
            wraplength=235,
            height=2
        ).pack(fill="x", padx=14)

        bottom = tk.Frame(content, bg=WHITE)
        bottom.pack(fill="x", padx=14, pady=(9, 12))
        tk.Label(
            bottom,
            text=f"₹ {item['price']:.2f}",
            bg=WHITE,
            fg="#171717",
            font=(self.heading_font, 16, "bold")
        ).pack(side="left")

        self.animated_button(
            bottom,
            "ADD TO CART  +",
            lambda p=item: self.order_now(p),
            width=140,
            height=39
        ).pack(side="right")

    def _draw_card_surface(self, canvas: tk.Canvas, width: int, height: int, hovered: bool):
        if not canvas.winfo_exists() or width < 20 or height < 20:
            return
        canvas.delete("surface")
        color = "#FFD2DA" if hovered else "#E7E4E4"
        self.rounded_rect(
            canvas, 1, 1, width - 2, height - 2, radius=20,
            fill=WHITE, outline=color, width=2 if hovered else 1, tags="surface"
        )
        canvas.tag_lower("surface")

    def order_now(self, item: dict):
        self.backend.cart.add(item)
        self.update_cart_button()
        self.show_add_feedback(item)

    def show_add_feedback(self, item: dict):
        if not hasattr(self, "page_host") or not self.page_host.winfo_exists():
            return
        if hasattr(self, "add_feedback") and self.add_feedback.winfo_exists():
            self.add_feedback.destroy()
        self.add_feedback = tk.Label(
            self.shell,
            text=f"✓  {item['name']} added to cart",
            bg="#202020",
            fg=WHITE,
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10
        )
        self.add_feedback.place(relx=0.98, rely=0.98, anchor="se")
        self.add_feedback.after(
            1600,
            lambda: self.add_feedback.destroy() if getattr(self, "add_feedback", None) and self.add_feedback.winfo_exists() else None
        )

    def show_checkout(self):
        self.clear_page()
        page = tk.Frame(self.page_host, bg=BG)
        page.pack(fill="both", expand=True, padx=45, pady=26)

        nav = tk.Frame(page, bg=BG)
        nav.pack(fill="x", pady=(0, 20))
        tk.Button(
            nav,
            text="← BACK TO MENU",
            command=self.show_menu,
            bg=WHITE,
            fg=RED,
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=9,
            cursor="hand2"
        ).pack(side="left")
        tk.Label(nav, text="CHECKOUT", bg=BG, fg=DARK, font=(self.heading_font, 27, "bold")).pack(side="right")

        if self.backend.cart.is_empty():
            tk.Label(page, text="Your cart is empty 🍗", bg=BG, fg=MUTED, font=("Arial", 17, "bold")).pack(pady=70)
            tk.Button(page, text="EXPLORE MENU", command=self.show_menu, bg=RED, fg=WHITE, relief="flat", padx=20, pady=12).pack()
            return

        columns = tk.Frame(page, bg=BG)
        columns.pack(fill="both", expand=True)

        summary = tk.Frame(columns, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        summary.pack(side="left", fill="both", expand=True, padx=(0, 18))
        details = tk.Frame(columns, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        details.pack(side="left", fill="y", ipadx=10)

        tk.Label(
            summary, text="YOUR ORDER  🍗", bg=WHITE, fg=DARK, font=(self.heading_font, 19, "bold")
        ).pack(anchor="w", padx=22, pady=(20, 12))

        self.checkout_items = tk.Frame(summary, bg=WHITE)
        self.checkout_items.pack(fill="x", padx=22)

        self.checkout_total = tk.Label(summary, text="", bg=WHITE, fg=RED, font=("Arial", 17, "bold"))
        self.checkout_total.pack(anchor="e", padx=22, pady=20)
        self.render_checkout_items()

        tk.Label(
            details, text="DELIVERY DETAILS", bg=WHITE, fg=RED, font=(self.heading_font, 18, "bold")
        ).pack(anchor="w", padx=22, pady=(20, 5))
        tk.Label(
            details, text="Where should we bring your food?", bg=WHITE, fg=MUTED, font=("Arial", 9)
        ).pack(anchor="w", padx=22, pady=(0, 10))

        self.name_entry = self.form_entry(details, "Full name")
        self.phone_entry = self.form_entry(details, "10-digit mobile number")
        self.address_entry = self.form_entry(details, "Delivery address", multiline=True)

        tk.Label(details, text="PAYMENT METHOD", bg=WHITE, fg=DARK, font=("Arial", 9, "bold")).pack(anchor="w", padx=22, pady=(12, 5))
        self.payment_var = tk.StringVar(value="Cash on Delivery")
        ttk.Combobox(
            details,
            textvariable=self.payment_var,
            values=["Cash on Delivery", "UPI (demo only)"],
            state="readonly",
            width=28
        ).pack(anchor="w", padx=22, ipady=5)

        tk.Button(
            details,
            text="PLACE DEMO ORDER  →",
            command=self.submit_order,
            bg=RED,
            fg=WHITE,
            activebackground="#B90024",
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=13,
            cursor="hand2"
        ).pack(fill="x", padx=22, pady=24)

    def form_entry(self, parent, label: str, multiline: bool = False):
        tk.Label(parent, text=label, bg=WHITE, fg=DARK, font=("Arial", 9, "bold")).pack(anchor="w", padx=22, pady=(9, 4))
        if multiline:
            widget = tk.Text(parent, height=4, width=31, font=("Arial", 10), relief="solid", bd=1, wrap="word")
        else:
            widget = tk.Entry(parent, width=34, font=("Arial", 10), relief="solid", bd=1)
        widget.pack(anchor="w", padx=22, ipady=7 if not multiline else 2)
        return widget

    def render_checkout_items(self):
        for child in self.checkout_items.winfo_children():
            child.destroy()

        for name, item in self.backend.cart.get_items().items():
            row = tk.Frame(self.checkout_items, bg=WHITE)
            row.pack(fill="x", pady=8)
            tk.Label(
                row,
                text=f"{item['emoji']}  {name}",
                bg=WHITE,
                fg=DARK,
                font=("Arial", 10, "bold"),
                wraplength=260,
                justify="left"
            ).pack(side="left")

            tk.Label(
                row,
                text=f"₹{item['price'] * item['qty']}",
                bg=WHITE,
                fg=DARK,
                font=("Arial", 10, "bold")
            ).pack(side="right")

            controls = tk.Frame(self.checkout_items, bg=WHITE)
            controls.pack(anchor="w", pady=(0, 5))
            tk.Button(controls, text="−", width=3, command=lambda n=name: self.checkout_change_qty(n, -1)).pack(side="left")
            tk.Label(controls, text=f"  {item['qty']}  ", bg=WHITE, font=("Arial", 9, "bold")).pack(side="left")
            tk.Button(controls, text="+", width=3, command=lambda n=name: self.checkout_change_qty(n, 1)).pack(side="left")

        self.checkout_total.configure(text=f"TOTAL: ₹{self.backend.cart.get_total():.2f}")

    def checkout_change_qty(self, name: str, delta: int):
        self.backend.cart.change_qty(name, delta)
        self.update_cart_button()
        self.show_checkout()

    def submit_order(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get("1.0", "end").strip()
        payment = self.payment_var.get()

        result = self.backend.place_order(name=name, phone=phone, address=address, payment_method=payment)
        if not result["success"]:
            messagebox.showwarning("Notice", result["error"])
            return

        messagebox.showinfo(
            "Order placed!",
            f"Thank you, {result['customer_name']}! 🍗\n\n"
            f"Order ID: {result['order_code']}\n"
            f"Total: ₹{result['total']:.2f}\n\n"
            f"Your demo order has been saved."
        )
        self.update_cart_button()
        self.show_menu()

    def open_order_history(self):
        win = tk.Toplevel(self.root)
        win.title("Order History")
        win.geometry("800x520")
        win.configure(bg=WHITE)
        win.transient(self.root)

        tk.Label(
            win, text="YOUR PREVIOUS ORDERS", bg=WHITE, fg=RED, font=("Arial", 19, "bold")
        ).pack(anchor="w", padx=22, pady=(20, 5))
        tk.Label(
            win, text="Search using the mobile number entered at checkout.", bg=WHITE, fg=MUTED, font=("Arial", 9)
        ).pack(anchor="w", padx=22)

        search = tk.Frame(win, bg=WHITE)
        search.pack(fill="x", padx=22, pady=15)
        phone = tk.Entry(search, font=("Arial", 11), relief="solid", bd=1)
        phone.pack(side="left", fill="x", expand=True, ipady=8)

        results = tk.Frame(win, bg=WHITE)
        results.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        def search_history():
            number = phone.get().strip()
            success, rows_or_msg = self.backend.get_order_history(number)
            if not success:
                messagebox.showwarning("Notice", rows_or_msg, parent=win)
                return

            for child in results.winfo_children():
                child.destroy()

            rows = rows_or_msg
            if not rows:
                tk.Label(results, text="No previous orders found.", bg=WHITE, fg=MUTED, font=("Arial", 11)).pack(pady=25)
                return

            table = ttk.Treeview(
                results,
                columns=("code", "date", "total", "payment", "status"),
                show="headings",
                height=10
            )
            for col, title, width in [
                ("code", "Order ID", 190),
                ("date", "Date", 150),
                ("total", "Total", 100),
                ("payment", "Payment", 140),
                ("status", "Status", 100)
            ]:
                table.heading(col, text=title)
                table.column(col, width=width, anchor="center")
            table.pack(fill="both", expand=True)

            for row in rows:
                table.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(
                        row["order_code"],
                        row["order_date"],
                        f"₹{row['total']:.2f}",
                        row["payment_method"],
                        row["status"]
                    )
                )

            def show_items(_event=None):
                selected = table.selection()
                if not selected:
                    return
                order_id = int(selected[0])
                items = self.backend.get_order_items(order_id)
                details = "\n".join(
                    f"{i['product_name']} × {i['quantity']} = ₹{i['quantity'] * i['unit_price']:.2f}"
                    for i in items
                )
                messagebox.showinfo("Order items", details or "No items found.", parent=win)

            table.bind("<<TreeviewSelect>>", show_items)

        tk.Button(
            search,
            text="SEARCH",
            command=search_history,
            bg=RED,
            fg=WHITE,
            relief="flat",
            padx=18,
            pady=9,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(8, 0))
