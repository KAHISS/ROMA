(function () {
  const form = document.querySelector("[data-sale-item-form]");
  if (!form) return;

  const barcodeInput = form.querySelector("[name='barcode']");
  const submitButton = form.querySelector("[data-sale-item-submit]");
  const itemsBody = document.querySelector("[data-sale-items]");
  const feedback = document.querySelector("[data-sale-item-feedback]");
  const totalQuantity = document.querySelector("[data-sale-total-quantity]");
  const subtotal = document.querySelector("[data-sale-subtotal]");
  const total = document.querySelector("[data-sale-total]");
  const summaryForm = document.querySelector("[data-sale-summary-form]");
  const summaryFeedback = document.querySelector("[data-sale-summary-feedback]");
  const discount = document.querySelector("[data-sale-discount]");
  const freight = document.querySelector("[data-sale-freight]");
  const paymentMethod = document.querySelector("[name='payment_method']");
  const cashReceivedField = document.querySelector("[data-cash-received-field]");
  const cashReceived = document.querySelector("[name='cash_received']");
  const changeRow = document.querySelector("[data-change-row]");
  const changeValue = document.querySelector("[data-sale-change]");
  const productModal = document.querySelector("[data-product-search-modal]");
  const productSearchForm = document.querySelector("[data-product-search-form]");
  const productSearchInput = document.querySelector("[data-product-search-input]");
  const productSearchResults = document.querySelector("[data-product-search-results]");
  const productSearchFeedback = document.querySelector("[data-product-search-feedback]");

  function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
      const [key, value] = cookie.trim().split("=");
      if (key === name) return decodeURIComponent(value);
    }
    return "";
  }

  async function readJsonResponse(response, fallbackMessage) {
    const body = await response.text();

    try {
      return JSON.parse(body);
    } catch (error) {
      if (response.redirected || response.url.includes("/login")) {
        throw new Error("Sessão expirada. Recarregue a página e tente novamente.");
      }
      if (response.status === 403) {
        throw new Error("Sessão expirada ou requisição bloqueada. Recarregue a página.");
      }
      throw new Error(`${fallbackMessage} (resposta ${response.status}).`);
    }
  }

  function setFeedback(message, isError) {
    feedback.textContent = message;
    feedback.classList.remove("hidden", "text-red-600", "text-green-600", "dark:text-red-400", "dark:text-green-400");
    feedback.classList.add(isError ? "text-red-600" : "text-green-600");
    feedback.classList.add(isError ? "dark:text-red-400" : "dark:text-green-400");
  }

  function createCell(text, className) {
    const cell = document.createElement("td");
    cell.className = className;
    cell.textContent = text;
    return cell;
  }

  function updateSaleTotals(sale) {
    totalQuantity.textContent = sale.total_quantity;
    subtotal.textContent = sale.subtotal;
    total.textContent = sale.total_price;
    if (paymentMethod && cashReceivedField && cashReceived && changeRow) updateChange();
  }

  function setSummaryFeedback(message, isError) {
    summaryFeedback.textContent = message;
    summaryFeedback.classList.remove("hidden", "text-red-600", "text-green-600", "dark:text-red-400", "dark:text-green-400");
    summaryFeedback.classList.add(isError ? "text-red-600" : "text-green-600");
    summaryFeedback.classList.add(isError ? "dark:text-red-400" : "dark:text-green-400");
  }

  function parseMoney(value) {
    return Number.parseFloat(String(value || "0").replace(",", ".")) || 0;
  }

  function formatMoney(value) {
    return `R$ ${value.toFixed(2).replace(".", ",")}`;
  }

  function updateChange() {
    const isCash = paymentMethod.value === "dinheiro";
    cashReceivedField.classList.toggle("hidden", !isCash);
    changeRow.classList.toggle("hidden", !isCash);
    if (!isCash) {
      cashReceived.value = "0.00";
      return;
    }

    const change = Math.max(0, parseMoney(cashReceived.value) - parseMoney(total.textContent.replace("R$", "")));
    changeValue.textContent = formatMoney(change);
  }

  function setProductSearchFeedback(message, isError) {
    productSearchFeedback.textContent = message;
    productSearchFeedback.classList.remove("hidden", "text-red-600", "text-gray-500", "dark:text-red-400", "dark:text-neutral-400");
    productSearchFeedback.classList.add(isError ? "text-red-600" : "text-gray-500");
    productSearchFeedback.classList.add(isError ? "dark:text-red-400" : "dark:text-neutral-400");
  }

  function renderProductResults(products) {
    productSearchResults.innerHTML = "";
    if (!products.length) {
      setProductSearchFeedback("Nenhum produto encontrado.", false);
      return;
    }

    products.forEach(function (product) {
      const row = document.createElement("div");
      row.className = "flex items-center justify-between gap-3 rounded-md border border-gray-200 p-3 dark:border-neutral-800";

      const info = document.createElement("div");
      info.className = "min-w-0";
      const description = document.createElement("div");
      description.className = "truncate text-sm font-medium text-gray-900 dark:text-neutral-100";
      description.textContent = product.description;
      const details = document.createElement("div");
      details.className = "mt-1 text-xs text-gray-500 dark:text-neutral-400";
      details.textContent = `${product.brand ? `${product.brand} · ` : ""}${product.barcode || "Sem código"} · Estoque: ${product.quantity}`;
      info.append(description, details);

      const action = document.createElement("div");
      action.className = "flex shrink-0 items-center gap-3";
      const price = document.createElement("span");
      price.className = "font-mono text-xs font-semibold text-gray-700 dark:text-neutral-200";
      price.textContent = product.price;
      const addButton = document.createElement("button");
      addButton.type = "button";
      addButton.className = "rounded-md bg-amber-500 px-3 py-1.5 text-xs font-semibold text-black hover:bg-amber-400";
      addButton.textContent = "Adicionar";
      addButton.addEventListener("click", function () {
        addManualProduct(product.id, addButton);
      });
      action.append(price, addButton);
      row.append(info, action);
      productSearchResults.appendChild(row);
    });
  }

  async function addManualProduct(productId, button) {
    button.disabled = true;
    try {
      const response = await fetch(productModal.dataset.addUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: new URLSearchParams({ product_id: productId }),
      });
      const data = await readJsonResponse(response, "Não foi possível adicionar o produto");
      if (!response.ok) throw new Error(data.error || "Não foi possível adicionar o produto.");
      updateItemRow(data.item);
      updateSaleTotals(data.sale);
      setFeedback("Produto adicionado à venda.", false);
      closeProductModal();
    } catch (error) {
      setProductSearchFeedback(error.message, true);
    } finally {
      button.disabled = false;
    }
  }

  function openProductModal() {
    productModal.classList.remove("hidden");
    productModal.classList.add("flex");
    productSearchInput.focus();
  }

  function closeProductModal() {
    productModal.classList.add("hidden");
    productModal.classList.remove("flex");
    productSearchInput.value = "";
    productSearchResults.innerHTML = "";
    productSearchFeedback.classList.add("hidden");
  }

  function createQuantityCell(item) {
    const cell = document.createElement("td");
    cell.className = "px-3.5 py-3 text-right text-gray-700 dark:text-neutral-200";

    const control = document.createElement("div");
    control.className = "inline-flex items-center rounded-md border border-gray-200 dark:border-neutral-700";
    control.dataset.itemQuantityControl = "true";
    control.dataset.quantityUrl = item.quantity_url;

    const decrease = document.createElement("button");
    decrease.type = "button";
    decrease.dataset.quantityChange = "-1";
    decrease.className = "flex h-7 w-7 items-center justify-center text-gray-500 transition-colors hover:bg-gray-100 hover:text-amber-600 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-amber-400";
    decrease.setAttribute("aria-label", "Diminuir quantidade");
    decrease.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/></svg>';

    const quantity = document.createElement("span");
    quantity.dataset.itemQuantity = "true";
    quantity.className = "min-w-8 px-1 text-center text-xs font-semibold";
    quantity.textContent = item.quantity;

    const increase = document.createElement("button");
    increase.type = "button";
    increase.dataset.quantityChange = "1";
    increase.className = decrease.className;
    increase.setAttribute("aria-label", "Aumentar quantidade");
    increase.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>';

    control.append(decrease, quantity, increase);
    cell.appendChild(control);
    return cell;
  }

  function updateItemRow(item) {
    const currentRow = itemsBody.querySelector(`[data-sale-item-id='${item.id}']`);
    if (currentRow) {
      currentRow.querySelector("[data-item-quantity]").textContent = item.quantity;
      currentRow.querySelector("[data-item-subtotal]").textContent = item.subtotal;
      return;
    }

    const emptyRow = itemsBody.querySelector("[data-sale-empty]")?.closest("tr");
    if (emptyRow) emptyRow.remove();

    const row = document.createElement("tr");
    row.dataset.saleItemId = item.id;
    row.className = "border-b border-gray-100 last:border-0 dark:border-neutral-800/70";

    const productCell = document.createElement("td");
    productCell.className = "px-3.5 py-3";
    const description = document.createElement("div");
    description.className = "font-medium text-gray-900 dark:text-neutral-100";
    description.textContent = item.description;
    productCell.appendChild(description);
    if (item.brand) {
      const brand = document.createElement("div");
      brand.className = "mt-0.5 text-xs text-gray-500 dark:text-neutral-400";
      brand.textContent = item.brand;
      productCell.appendChild(brand);
    }

    row.appendChild(productCell);
    row.appendChild(createCell(item.barcode, "px-3.5 py-3 font-mono text-xs text-gray-500 dark:text-neutral-400"));
    row.appendChild(createQuantityCell(item));
    row.appendChild(createCell(item.subtotal, "px-3.5 py-3 text-right font-medium text-gray-900 dark:text-neutral-100"));
    row.lastChild.dataset.itemSubtotal = "true";
    itemsBody.appendChild(row);
  }

  async function changeQuantity(button) {
    const control = button.closest("[data-item-quantity-control]");
    const row = button.closest("[data-sale-item-id]");
    const delta = button.dataset.quantityChange;
    button.disabled = true;

    try {
      const response = await fetch(control.dataset.quantityUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: new URLSearchParams({ delta }),
      });
      const data = await readJsonResponse(response, "Não foi possível alterar a quantidade");
      if (!response.ok) throw new Error(data.error || "Não foi possível alterar a quantidade.");

      if (data.item) {
        row.querySelector("[data-item-quantity]").textContent = data.item.quantity;
        row.querySelector("[data-item-subtotal]").textContent = data.item.subtotal;
      } else {
        row.remove();
      }
      updateSaleTotals(data.sale);
    } catch (error) {
      setFeedback(error.message, true);
    } finally {
      button.disabled = false;
    }
  }

  itemsBody.addEventListener("click", function (event) {
    const button = event.target.closest("[data-quantity-change]");
    if (button) changeQuantity(button);
  });

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const barcode = barcodeInput.value.trim();
    if (!barcode) {
      setFeedback("Informe o código de barras.", true);
      barcodeInput.focus();
      return;
    }

    submitButton.disabled = true;
    submitButton.classList.add("opacity-60", "cursor-wait");

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: new URLSearchParams({ barcode }),
      });
      const data = await readJsonResponse(response, "Não foi possível adicionar o produto");
      if (!response.ok) throw new Error(data.error || "Não foi possível adicionar o produto.");

      updateItemRow(data.item);
      updateSaleTotals(data.sale);
      setFeedback("Produto adicionado à venda.", false);
      barcodeInput.value = "";
      barcodeInput.focus();
    } catch (error) {
      setFeedback(error.message, true);
      barcodeInput.select();
    } finally {
      submitButton.disabled = false;
      submitButton.classList.remove("opacity-60", "cursor-wait");
    }
  });

  if (summaryForm) {
    summaryForm.querySelectorAll("input, select").forEach(function (field) {
      field.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
          summaryForm.requestSubmit();
        }
      });
    });

    summaryForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      const submitButton = summaryForm.querySelector("button[type='submit']");
      submitButton.disabled = true;
      submitButton.classList.add("opacity-60", "cursor-wait");

      try {
        const response = await fetch(summaryForm.getAttribute("action"), {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: new URLSearchParams(new FormData(summaryForm)),
        });
        const data = await readJsonResponse(response, "Não foi possível atualizar o resumo");
        if (!response.ok) throw new Error(data.error || "Não foi possível atualizar o resumo.");

        subtotal.textContent = data.sale.subtotal;
        discount.textContent = `- ${data.sale.discount}`;
        freight.textContent = data.sale.freight;
        total.textContent = data.sale.total_price;
        updateChange();
        setSummaryFeedback("Resumo atualizado.", false);
      } catch (error) {
        setSummaryFeedback(error.message, true);
      } finally {
        submitButton.disabled = false;
        submitButton.classList.remove("opacity-60", "cursor-wait");
      }
    });
  }

  if (productModal) {
    document.querySelector("[data-open-product-search]").addEventListener("click", openProductModal);
    document.querySelector("[data-close-product-search]").addEventListener("click", closeProductModal);
    productModal.addEventListener("click", function (event) {
      if (event.target === productModal) closeProductModal();
    });
    productSearchForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      const query = productSearchInput.value.trim();
      if (!query) {
        setProductSearchFeedback("Digite uma descrição, marca ou código.", true);
        return;
      }
      try {
        const response = await fetch(`${productModal.dataset.searchUrl}?q=${encodeURIComponent(query)}`, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const data = await readJsonResponse(response, "Não foi possível buscar produtos");
        if (!response.ok) throw new Error(data.error || "Não foi possível buscar produtos.");
        setProductSearchFeedback(`${data.products.length} produto(s) encontrado(s).`, false);
        renderProductResults(data.products);
      } catch (error) {
        setProductSearchFeedback(error.message, true);
      }
    });
  }

  if (paymentMethod && cashReceivedField && cashReceived && changeRow) {
    paymentMethod.addEventListener("change", updateChange);
    cashReceived.addEventListener("input", updateChange);
    updateChange();
  }
})();