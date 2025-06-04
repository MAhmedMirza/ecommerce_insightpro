document.addEventListener("DOMContentLoaded", function () {
  // Input field animations
  const inputs = document.querySelectorAll(".form-control");
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.style.animation = "pulse 1.5s infinite";
    });

    input.addEventListener("blur", function () {
      this.style.animation = "none";
    });

    // Clear error state when typing
    input.addEventListener("input", function () {
      if (this.classList.contains("is-invalid")) {
        this.classList.remove("is-invalid");
        const errorMsg =
          this.nextElementSibling?.querySelector(".error-message");
        if (errorMsg) errorMsg.textContent = "";
      }
    });
  });

  // Floating animation for header
  const header = document.querySelector(".login-header");
  if (header) {
    header.style.animation = "float 6s ease-in-out infinite";
  }

  // Close when clicking outside
  document.body.addEventListener("click", function (e) {
    if (e.target === document.body) {
      window.history.back();
    }
  });

  // Highlight fields with errors
  const errorFields = document.querySelectorAll(".error-message");
  errorFields.forEach((error) => {
    if (error.textContent.trim() !== "") {
      const input = error.closest(".form-group").querySelector(".form-control");
      if (input) input.classList.add("is-invalid");
    }
  });
});
