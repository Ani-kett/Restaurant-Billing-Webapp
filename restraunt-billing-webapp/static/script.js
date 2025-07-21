let order = {};  // Format: { itemId: { name, qty, price } }

function addToOrder(name, price, id) {
  const input = document.querySelector(`input[name="${id}"]`);
  let qty = parseInt(input.value);
  if (isNaN(qty) || qty <= 0) {
    alert("Please enter a valid quantity");
    return;
  }

  if (order[id]) {
    order[id].qty += qty;
  } else {
    order[id] = { name, qty, price };
  }

  input.value = 0;  // Reset input
  updateOrderList();
}

function removeItem(id) {
  if (order[id]) {
    order[id].qty -= 1;
    if (order[id].qty <= 0) {
      delete order[id];
    }
    updateOrderList();
  }
}

function updateOrderList() {
  const list = document.getElementById("order-list");
  const totalDisplay = document.getElementById("order-total");

  list.innerHTML = "";
  let total = 0;

  for (const id in order) {
    const item = order[id];
    const li = document.createElement("li");
    li.textContent = `${item.name} x ${item.qty} = ₹${item.qty * item.price}`;
    
    const removeBtn = document.createElement("button");
    removeBtn.textContent = " - ";
    removeBtn.onclick = () => removeItem(id);
    removeBtn.className = "remove-btn";

    li.appendChild(removeBtn);
    list.appendChild(li);
    total += item.qty * item.price;

    // Update hidden input in form so Flask gets the quantity
    let hiddenInput = document.querySelector(`input[name="${id}"]`);
    if (hiddenInput) {
      hiddenInput.value = item.qty;
    }
  }

  totalDisplay.textContent = total > 0 ? `Total: ₹${total}` : "";
}

// Handle collapsibles
document.querySelectorAll(".collapsible").forEach(btn => {
  btn.addEventListener("click", () => {
    btn.classList.toggle("active");
    const content = btn.nextElementSibling;
    content.style.display = content.style.display === "block" ? "none" : "block";
  });
});

// Re-add individual item from previous orders
document.querySelectorAll(".re-add-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const name = btn.dataset.name;
    const price = parseFloat(btn.dataset.price);
    const id = btn.dataset.id;
    const quantity = parseInt(btn.dataset.quantity);
    for (let i = 0; i < quantity; i++) {
      addToOrder(name, price, id);
    }
  });
});

// Reorder the entire previous bill
document.querySelectorAll(".reorder-bill").forEach(btn => {
  btn.addEventListener("click", () => {
    const items = JSON.parse(btn.dataset.items);
    items.forEach(item => {
      for (let i = 0; i < item.quantity; i++) {
        addToOrder(item.name, item.price, item.id);
      }
    });
  });
});