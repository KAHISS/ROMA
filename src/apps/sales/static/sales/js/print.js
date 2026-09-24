(function () {
  document.querySelectorAll("[data-print-sale-url]").forEach(function (button) {
    button.addEventListener("click", function () {
      window.open(button.dataset.printSaleUrl, "_blank", "noopener,noreferrer");
    });
  });

  const printButton = document.querySelector("[data-print-current-sale]");
  if (printButton) printButton.addEventListener("click", function () { window.print(); });

  if (new URLSearchParams(window.location.search).get("print") === "1") {
    window.addEventListener("load", function () { window.print(); });
  }
})();