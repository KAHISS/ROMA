document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("userModal");
  const openButton = document.getElementById("openUserModal");
  const passwordModal = document.getElementById("passwordModal");

  const setupPasswordModal = () => {
    if (!passwordModal) {
      return;
    }

    const form = passwordModal.querySelector("form");
    const userIdField = form?.querySelector('[name="user_id"]');
    const closeButtons = passwordModal.querySelectorAll("[data-password-modal-close]");
    const passwordFields = form?.querySelectorAll('input[type="password"]') || [];
    let previouslyFocusedElement = null;

    const openPasswordModal = (button) => {
      const userId = button.dataset.userId;

      if (!userId) {
        return;
      }

      previouslyFocusedElement = document.activeElement;

      form?.reset();

      if (userIdField) {
        userIdField.value = userId;
      }

      passwordModal.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");
      passwordFields[0]?.focus();
    };

    const closePasswordModal = () => {
      passwordModal.classList.add("hidden");
      document.body.classList.remove("overflow-hidden");
      previouslyFocusedElement?.focus();
    };

    document.querySelectorAll("[data-user-set-password]").forEach((button) => {
      button.addEventListener("click", () => {
        openPasswordModal(button);
      });
    });

    closeButtons.forEach((button) => {
      button.addEventListener("click", closePasswordModal);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !passwordModal.classList.contains("hidden")) {
        closePasswordModal();
      }
    });
  };

  setupPasswordModal();

  if (!modal || !openButton) {
    return;
  }

  const form = modal.querySelector("form");
  const title = document.getElementById("userModalTitle");
  const description = title?.nextElementSibling;
  const submitButton = form?.querySelector('button[type="submit"]');
  const userIdField = form?.querySelector('[name="user_id"]');
  const closeButtons = modal.querySelectorAll("[data-user-modal-close]");
  const passwordFields = modal.querySelectorAll("[data-user-password-field]");
  const fields = {
    firstName: form?.querySelector('[name="first_name"]'),
    lastName: form?.querySelector('[name="last_name"]'),
    username: form?.querySelector('[name="username"]'),
    email: form?.querySelector('[name="email"]'),
    isSuperuser: form?.querySelector('[name="is_superuser"]'),
    password1: form?.querySelector('[name="password1"]'),
    password2: form?.querySelector('[name="password2"]'),
  };
  let previouslyFocusedElement = null;

  const openModal = () => {
    previouslyFocusedElement = document.activeElement;
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    fields.firstName?.focus();
  };

  const closeModal = () => {
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    previouslyFocusedElement?.focus();
  };

  const setPasswordFieldsVisibility = (visible) => {
    passwordFields.forEach((field) => {
      field.classList.toggle("hidden", !visible);
    });

    if (fields.password1) {
      fields.password1.required = visible;
      fields.password1.disabled = !visible;
      fields.password1.value = "";
    }

    if (fields.password2) {
      fields.password2.required = visible;
      fields.password2.disabled = !visible;
      fields.password2.value = "";
    }
  };

  const setCreateMode = () => {
    form?.reset();
    form?.removeAttribute("data-user-id");
    if (userIdField) userIdField.value = "";

    setPasswordFieldsVisibility(true);

    if (title) title.textContent = "Novo usuário";
    if (description) {
      description.textContent =
        "Preencha os dados para cadastrar um novo usuário no sistema.";
    }
    if (submitButton) submitButton.textContent = "Cadastrar usuário";
  };

  const setEditMode = (button) => {
    form?.reset();

    if (title) title.textContent = "Editar usuário";
    if (description) {
      description.textContent = "Atualize os dados do usuário selecionado.";
    }
    if (submitButton) submitButton.textContent = "Salvar alterações";

    setPasswordFieldsVisibility(false);

    form?.setAttribute("data-user-id", button.dataset.userId || "");
    if (userIdField) userIdField.value = button.dataset.userId || "";
    if (fields.firstName) fields.firstName.value = button.dataset.firstName || "";
    if (fields.lastName) fields.lastName.value = button.dataset.lastName || "";
    if (fields.username) fields.username.value = button.dataset.username || "";
    if (fields.email) fields.email.value = button.dataset.email || "";
    if (fields.isSuperuser) {
      fields.isSuperuser.checked = button.dataset.isSuperuser === "true";
    }
  };

  openButton.addEventListener("click", () => {
    setCreateMode();
    openModal();
  });

  document.querySelectorAll("[data-user-edit]").forEach((button) => {
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