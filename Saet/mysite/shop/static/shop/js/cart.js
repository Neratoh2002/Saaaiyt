// Утилита: CSRF из cookie
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
  return null;
}
const csrftoken = getCookie("csrftoken");

// Фетч-обертки
async function apiGet(url) {
  const res = await fetch(url, { credentials: "same-origin" });
  return res.json();
}
async function apiPost(url, data = {}) {
  const res = await fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken || "",
    },
    body: JSON.stringify(data),
  });
  return res.json();
}

// Отрисовка счетчика в шапке
function updateNavCartCount(items) {
  const count = items.reduce((acc, it) => acc + (parseInt(it.quantity, 10) || 0), 0);
  const el = document.getElementById("nav-cart-count");
  if (el) el.textContent = count;
}

// Листинг и обновление корзины на странице /cart/
async function renderCart() {
  const container = document.getElementById("cart-container");
  if (!container) return;

  const data = await apiGet("/api/cart/");
  updateNavCartCount(data.items);

  if (!data.items.length) {
    container.innerHTML = `<p>Ваша корзина пуста.</p>`;
    return;
  }

  const rows = data.items.map(
    (it) => `
    <div class="cart-row" data-id="${it.id}">
      <div class="cart-col cart-product">
        ${it.image_url ? `<img src="${it.image_url}" alt="${it.name}">` : `<div class="placeholder sm">No Image</div>`}
        <div>
          <div class="cart-name">${it.name}</div>
          <div class="cart-price">${it.price} ₽</div>
        </div>
      </div>
      <div class="cart-col cart-qty">
        <input type="number" min="1" value="${it.quantity}" class="qty-input"/>
      </div>
      <div class="cart-col cart-subtotal">${it.subtotal} ₽</div>
      <div class="cart-col cart-actions">
        <button class="btn btn-danger remove-btn">×</button>
      </div>
    </div>`
  ).join("");

  container.innerHTML = `
    <div class="cart-rows">${rows}</div>
    <div class="cart-total">Итого: <strong>${data.total} ₽</strong></div>
  `;

  // обработчики
  container.querySelectorAll(".qty-input").forEach(input => {
    input.addEventListener("input", async (e) => {
      const row = e.target.closest(".cart-row");
      const id = parseInt(row.dataset.id, 10);
      let qty = parseInt(e.target.value, 10);
      if (isNaN(qty) || qty < 1) qty = 1;
      await apiPost("/api/cart/update/", { product_id: id, quantity: qty });
      renderCart();
    });
  });

  container.querySelectorAll(".remove-btn").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const row = e.target.closest(".cart-row");
      const id = parseInt(row.dataset.id, 10);
      await apiPost("/api/cart/remove/", { product_id: id });
      renderCart();
    });
  });
}

// Кнопки "В корзину" на любой странице
function bindAddToCartButtons() {
  document.querySelectorAll(".add-to-cart").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const id = parseInt(e.currentTarget.dataset.id, 10);
      let qty = 1;
      const qtyInput = document.getElementById("qty");
      if (qtyInput) {
        const v = parseInt(qtyInput.value, 10);
        qty = isNaN(v) || v < 1 ? 1 : v;
      }
      const data = await apiPost("/api/cart/add/", { product_id: id, quantity: qty });
      updateNavCartCount(data.items);
      // Простейший UX-трик
      e.currentTarget.textContent = "В корзине!";
      setTimeout(() => (e.currentTarget.textContent = "В корзину"), 1200);
    });
  });
}

// Оформление заказа
function bindCheckout() {
  const form = document.getElementById("checkout-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {};
    const emailField = form.querySelector('input[name="email"]');
    if (emailField) {
      // простая фронт-валидация
      const email = emailField.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        alert("Введите корректный email");
        return;
      }
      payload.email = email;
    }
    const order = await apiPost("/api/checkout/", payload);
    if (order && order.id) {
      alert(`Заказ #${order.id} оформлен! Итого: ${order.total} ₽`);
      window.location.href = "/";
    } else {
      alert(order?.detail || "Не удалось оформить заказ");
    }
  });
}

// Инициализация
document.addEventListener("DOMContentLoaded", async () => {
  bindAddToCartButtons();
  bindCheckout();

  // обновим счетчик в шапке
  try {
    const data = await apiGet("/api/cart/");
    updateNavCartCount(data.items);
  } catch (e) {}

  // если на странице корзины — отрисовать содержимое
  await renderCart();
});
