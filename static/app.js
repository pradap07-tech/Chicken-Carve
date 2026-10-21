const state = {
  products: [],
  categories: [],
  activeCategory: "",
  search: "",
  sort: "name_asc",
  cart: { items: [], subtotal: 0, delivery_fee: 0, total: 0, count: 0 },
};

const fallbackImage = "/static/fallback-food.svg";
const imgWorker = new Worker("/static/imageWorker.js");
const pendingImageNodes = new Map();
let imageTaskId = 1;

const productsGrid = document.getElementById("products-grid");
const categoryFilters = document.getElementById("category-filters");
const searchInput = document.getElementById("search-input");
const sortSelect = document.getElementById("sort-select");
const cartItemsElement = document.getElementById("cart-items");
const subtotalElement = document.getElementById("subtotal");
const deliveryElement = document.getElementById("delivery-fee");
const totalElement = document.getElementById("total");
const cartCountElement = document.getElementById("cart-count");
const checkoutForm = document.getElementById("checkout-form");
const checkoutMessage = document.getElementById("checkout-message");
const ordersList = document.getElementById("orders-list");

const cartPanel = document.getElementById("cart-panel");
const cartToggle = document.getElementById("cart-toggle");

cartToggle.addEventListener("click", () => {
  cartPanel.scrollIntoView({ behavior: "smooth", block: "start" });
});

function debounce(fn, delay = 250) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

function currency(value) {
  return `$${Number(value).toFixed(2)}`;
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

imgWorker.onmessage = (event) => {
  const { id, status, src } = event.data;
  const target = pendingImageNodes.get(id);
  if (!target) return;

  if (status === "ok" && src) {
    target.src = src;
  } else {
    target.src = fallbackImage;
  }

  pendingImageNodes.delete(id);
};

function queueImageLoad(img, src) {
  const taskId = imageTaskId++;
  pendingImageNodes.set(taskId, img);
  imgWorker.postMessage({ id: taskId, url: src });
}

const lazyObserver = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.dataset.src;
        if (src) {
          queueImageLoad(img, src);
          delete img.dataset.src;
        }
        lazyObserver.unobserve(img);
      }
    }
  },
  { rootMargin: "200px" }
);

function renderProducts() {
  productsGrid.innerHTML = "";
  const template = document.getElementById("product-card-template");

  state.products.forEach((product) => {
    const node = template.content.cloneNode(true);

    const card = node.querySelector(".product-card");
    const image = node.querySelector(".food-image");
    const name = node.querySelector(".product-name");
    const description = node.querySelector(".product-description");
    const meta = node.querySelector(".product-meta");
    const price = node.querySelector(".product-price");
    const addBtn = node.querySelector(".add-btn");

    card.dataset.productId = product.id;
    image.alt = product.name;
    image.src = fallbackImage;
    image.dataset.src = product.image_url;
    lazyObserver.observe(image);

    name.textContent = product.name;
    description.textContent = product.description;
    meta.textContent = product.category;
    price.textContent = currency(product.price);

    addBtn.addEventListener("click", () => addToCart(product.id));

    productsGrid.appendChild(node);
  });
}

function renderCategories() {
  categoryFilters.innerHTML = "";
  const allButton = document.createElement("button");
  allButton.className = `category-chip ${state.activeCategory === "" ? "active" : ""}`;
  allButton.textContent = "All";
  allButton.addEventListener("click", () => {
    state.activeCategory = "";
    loadProducts();
  });
  categoryFilters.appendChild(allButton);

  state.categories.forEach((category) => {
    const button = document.createElement("button");
    button.className = `category-chip ${state.activeCategory === category ? "active" : ""}`;
    button.textContent = category;
    button.addEventListener("click", () => {
      state.activeCategory = category;
      loadProducts();
    });
    categoryFilters.appendChild(button);
  });
}

function renderCart() {
  cartItemsElement.innerHTML = "";

  if (state.cart.items.length === 0) {
    cartItemsElement.innerHTML = "<p>Your cart is empty.</p>";
  } else {
    state.cart.items.forEach((item) => {
      const row = document.createElement("div");
      row.className = "cart-item";
      row.innerHTML = `
        <div>
          <strong>${item.name}</strong>
          <p>${currency(item.price)} • ${currency(item.line_total)}</p>
          <div class="qty-controls">
            <button class="btn" data-action="decrease">-</button>
            <span>${item.quantity}</span>
            <button class="btn" data-action="increase">+</button>
            <button class="btn remove-btn" data-action="remove">Remove</button>
          </div>
        </div>
      `;

      row.querySelector('[data-action="decrease"]').addEventListener("click", () => {
        updateQuantity(item.id, item.quantity - 1);
      });
      row.querySelector('[data-action="increase"]').addEventListener("click", () => {
        updateQuantity(item.id, item.quantity + 1);
      });
      row.querySelector('[data-action="remove"]').addEventListener("click", () => {
        removeCartItem(item.id);
      });

      cartItemsElement.appendChild(row);
    });
  }

  subtotalElement.textContent = currency(state.cart.subtotal);
  deliveryElement.textContent = currency(state.cart.delivery_fee);
  totalElement.textContent = currency(state.cart.total);
  cartCountElement.textContent = state.cart.count;
}

function renderOrders(orders) {
  ordersList.innerHTML = "";
  if (orders.length === 0) {
    ordersList.innerHTML = "<p>No orders yet.</p>";
    return;
  }

  orders.forEach((order) => {
    const card = document.createElement("article");
    card.className = "order-card";
    const items = order.items.map((item) => `${item.quantity}× ${item.name}`).join(", ");
    card.innerHTML = `
      <strong>Order #${order.id} • ${currency(order.total)}</strong>
      <p>${new Date(order.created_at).toLocaleString()}</p>
      <p>${items}</p>
      <p>${order.customer_name} • ${order.phone}</p>
    `;
    ordersList.appendChild(card);
  });
}

async function loadProducts() {
  const query = new URLSearchParams({
    search: state.search,
    category: state.activeCategory,
    sort: state.sort,
  });

  const payload = await api(`/api/products?${query.toString()}`);
  state.products = payload.products;
  renderProducts();
  renderCategories();
}

async function loadCategories() {
  const payload = await api("/api/categories");
  state.categories = payload.categories;
  renderCategories();
}

async function loadCart() {
  state.cart = await api("/api/cart");
  renderCart();
}

async function loadOrders() {
  const payload = await api("/api/orders");
  renderOrders(payload.orders);
}

async function addToCart(productId) {
  state.cart = await api("/api/cart/add", {
    method: "POST",
    body: JSON.stringify({ product_id: productId, quantity: 1 }),
  });
  renderCart();
}

async function updateQuantity(productId, quantity) {
  state.cart = await api(`/api/cart/${productId}`, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
  renderCart();
}

async function removeCartItem(productId) {
  state.cart = await api(`/api/cart/${productId}`, { method: "DELETE" });
  renderCart();
}

searchInput.addEventListener(
  "input",
  debounce(() => {
    state.search = searchInput.value.trim();
    loadProducts();
  }, 250)
);

sortSelect.addEventListener("change", () => {
  state.sort = sortSelect.value;
  loadProducts();
});

checkoutForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  checkoutMessage.textContent = "";
  const formData = new FormData(checkoutForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    await api("/api/checkout", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    checkoutForm.reset();
    checkoutMessage.textContent = "Order placed successfully.";
    await Promise.all([loadCart(), loadOrders()]);
  } catch (error) {
    checkoutMessage.textContent = error.message;
  }
});

async function init() {
  try {
    await Promise.all([loadCategories(), loadCart(), loadOrders()]);
    await loadProducts();
  } catch (error) {
    checkoutMessage.textContent = error.message;
  }
}

init();
