document.addEventListener("DOMContentLoaded", function () {
  // Safe alert function with SweetAlert2 fallback
  function showAlert(title, text, icon, confirmText) {
    if (typeof Swal !== "undefined") {
      return Swal.fire({
        title: title,
        text: text,
        icon: icon,
        confirmButtonText: confirmText || "OK",
      });
    } else {
      alert(`${title}\n\n${text}`);
      return Promise.resolve({ isConfirmed: true });
    }
  }

  // DOM elements
  const container = document.querySelector(".container");
  const endpoints = {
    forgotPassword: container.dataset.forgotUrl,
    verifyCode: container.dataset.verifyUrl,
    resetPassword: container.dataset.resetUrl,
    loginUrl: container.dataset.loginUrl,
  };

  const step1 = document.getElementById("step1");
  const step2 = document.getElementById("step2");
  const step3 = document.getElementById("step3");
  const resetForm = document.getElementById("resetForm");
  const verifyForm = document.getElementById("verifyForm");
  const passwordForm = document.getElementById("passwordForm");
  const userEmail = document.getElementById("userEmail");
  const resendLink = document.getElementById("resendLink");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const confirmPasswordInput = document.getElementById("confirmPassword");
  const codeInputs = document.querySelectorAll(".code-input");
  const emailError = document.getElementById("emailError");
  const codeError = document.getElementById("codeError");
  const passwordError = document.getElementById("passwordError");

  let resetEmail = "";
  let verificationCode = "";

  // Loading state helper
  function setLoading(button, isLoading) {
    button.disabled = isLoading;
    button.innerHTML = isLoading
      ? '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...'
      : button.getAttribute("data-original-text");
  }

  // Store original button texts
  const resetBtn = resetForm.querySelector('button[type="submit"]');
  const verifyBtn = verifyForm.querySelector('button[type="submit"]');
  const passwordBtn = passwordForm.querySelector('button[type="submit"]');
  resetBtn.setAttribute("data-original-text", resetBtn.textContent);
  verifyBtn.setAttribute("data-original-text", verifyBtn.textContent);
  passwordBtn.setAttribute("data-original-text", passwordBtn.textContent);

  // Step 1: Request reset code
  resetForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    emailError.textContent = "";
    setLoading(resetBtn, true);

    try {
      const response = await fetch(endpoints.forgotPassword, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          email: emailInput.value,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Failed to send verification code");
      }

      const data = await response.json();
      resetEmail = emailInput.value;
      userEmail.textContent = resetEmail;
      step1.classList.add("hidden");
      step2.classList.remove("hidden");
      document.getElementById("code1").focus();
    } catch (error) {
      console.error("Error:", error);
      emailError.textContent = error.message;
      await showAlert("Error", error.message, "error");
      emailInput.focus();
    } finally {
      setLoading(resetBtn, false);
    }
  });

  // Step 2: Verify code
  verifyForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    codeError.textContent = "";
    setLoading(verifyBtn, true);

    const enteredCode = Array.from(codeInputs)
      .map((input) => input.value)
      .join("")
      .replace(/\D/g, "");

    try {
      const response = await fetch(endpoints.verifyCode, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: resetEmail,
          code: enteredCode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Invalid verification code");
      }

      const data = await response.json();

      if (data.success) {
        verificationCode = enteredCode;
        step2.classList.add("hidden");
        step3.classList.remove("hidden");
        passwordInput.focus();
        await showAlert(
          "Success!",
          "Code verified. Enter new password",
          "success"
        );
      } else {
        throw new Error(data.error || "Verification failed");
      }
    } catch (error) {
      console.error("Error:", error);
      codeError.textContent = error.message;
      codeInputs.forEach((input) => {
        input.value = "";
        input.classList.add("shake");
        setTimeout(() => input.classList.remove("shake"), 500);
      });
      document.getElementById("code1").focus();
    } finally {
      setLoading(verifyBtn, false);
    }
  });

  // Step 3: Reset password
  passwordForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    passwordError.textContent = "";
    setLoading(passwordBtn, true);

    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    // Client-side validation
    if (password !== confirmPassword) {
      passwordError.textContent = "Passwords do not match";
      confirmPasswordInput.focus();
      setLoading(passwordBtn, false);
      return;
    }
    if (password.length < 8) {
      passwordError.textContent = "Password must be at least 8 characters";
      passwordInput.focus();
      setLoading(passwordBtn, false);
      return;
    }

    try {
      const response = await fetch(endpoints.resetPassword, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: resetEmail,
          code: verificationCode,
          password: password,
          confirm_password: confirmPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Password reset failed");
      }

      const data = await response.json();

      if (data.success) {
        await showAlert(
          "Success!",
          "Password reset successfully! Redirecting to login...",
          "success"
        );
        window.location.href = endpoints.loginUrl;
      } else {
        throw new Error(data.error || "Failed to reset password");
      }
    } catch (error) {
      console.error("Error:", error);
      passwordError.textContent = error.message;
      passwordInput.classList.add("is-invalid");
      confirmPasswordInput.classList.add("is-invalid");
      passwordError.scrollIntoView({ behavior: "smooth", block: "center" });
    } finally {
      setLoading(passwordBtn, false);
    }
  });

  // Resend code link
  resendLink.addEventListener("click", async function (e) {
    e.preventDefault();
    if (!resetEmail) return;

    try {
      const response = await fetch(endpoints.forgotPassword, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: resetEmail,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Failed to resend code");
      }

      const data = await response.json();

      if (data.success) {
        await showAlert(
          "Code Sent!",
          "A new verification code has been sent to your email.",
          "success"
        );
      } else {
        throw new Error(data.error || "Failed to resend code");
      }
    } catch (error) {
      console.error("Error:", error);
      codeError.textContent = error.message;
    }
  });

  // Auto-focus between code inputs
  codeInputs.forEach((input, index) => {
    input.addEventListener("input", function () {
      if (this.value.length === 1 && index < codeInputs.length - 1) {
        codeInputs[index + 1].focus();
      }
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "Backspace" && this.value.length === 0 && index > 0) {
        codeInputs[index - 1].focus();
      }
    });
  });
});
