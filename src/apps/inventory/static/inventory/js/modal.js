document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("productModal");
  const openButton = document.getElementById("openProductModal");

  if (!modal || !openButton) {
    return;
  }

  const form = modal.querySelector("form");
  const title = document.getElementById("productModalTitle");
  const description = title?.nextElementSibling;
  const submitButton = form?.querySelector('button[type="submit"]');
  const productIdField = form?.querySelector('[name="product_id"]');
  const closeButtons = modal.querySelectorAll("[data-product-modal-close]");
  const fields = {
    barcode: form?.querySelector('[name="barcode"]'),
    description: form?.querySelector('[name="description"]'),
    brand: form?.querySelector('[name="brand"]'),
    cust: form?.querySelector('[name="cust"]'),
    price: form?.querySelector('[name="price"]'),
    quantity: form?.querySelector('[name="quantity"]'),
    minQuantity: form?.querySelector('[name="min_quantity"]'),
  };
  let previouslyFocusedElement = null;

  const openModal = () => {
    previouslyFocusedElement = document.activeElement;
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    fields.barcode?.focus();
  };

  const closeModal = () => {
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    previouslyFocusedElement?.focus();
  };

  const setCreateMode = () => {
    form?.reset();
    form?.removeAttribute("data-product-id");
    if (productIdField) productIdField.value = "";

    if (title) title.textContent = "Novo produto";
    if (description) {
      description.textContent =
        "Preencha os dados para cadastrar o produto no estoque.";
    }
    if (submitButton) submitButton.textContent = "Cadastrar produto";
  };

  const setEditMode = (button) => {
    if (title) title.textContent = "Editar produto";
    if (description) {
      description.textContent =
        "Atualize os dados do produto selecionado.";
    }
    if (submitButton) submitButton.textContent = "Salvar alterações";

    form?.setAttribute("data-product-id", button.dataset.productId);
    if (productIdField) productIdField.value = button.dataset.productId || "";
    if (fields.barcode) fields.barcode.value = button.dataset.barcode || "";
    if (fields.description) fields.description.value = button.dataset.description || "";
    if (fields.brand) fields.brand.value = button.dataset.brand || "";
    if (fields.cust) fields.cust.value = button.dataset.cust || "";
    if (fields.price) fields.price.value = button.dataset.price || "";
    if (fields.quantity) fields.quantity.value = button.dataset.quantity || "";
    if (fields.minQuantity) {
      fields.minQuantity.value = button.dataset.minQuantity || "";
    }
  };

  openButton.addEventListener("click", () => {
    setCreateMode();
    openModal();
  });

  document.querySelectorAll("[data-product-edit]").forEach((button) => {
    button.addEventListener("click", () => {
      setEditMode(button);
      openModal();
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });
});