document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("userModal");
  const openButton = document.getElementById("openUserModal");

  if (!modal || !openButton) {
    return;
  }

  const form = modal.querySelector("form");
  const closeButtons = modal.querySelectorAll("[data-user-modal-close]");
  const firstInput = form?.querySelector("input, select, textarea, button");
  let previouslyFocusedElement = null;

  const openModal = () => {
    previouslyFocusedElement = document.activeElement;
    form?.reset();
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    firstInput?.focus();
  };

  const closeModal = () => {
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    previouslyFocusedElement?.focus();
  };

  openButton.addEventListener("click", openModal);

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });
});