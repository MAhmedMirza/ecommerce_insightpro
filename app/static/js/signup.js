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
  });

  // Floating animation for header
  const header = document.querySelector(".signup-header");
  if (header) {
    header.style.animation = "float 6s ease-in-out infinite";
  }

  // Close when clicking outside
  document.body.addEventListener("click", function (e) {
    if (e.target === document.body) {
      window.history.back();
    }
  });

  // Form submission
  const signupForm = document.getElementById("signupForm");
  signupForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Here you would normally send the data to your server
    alert(
      `Signup submitted!\nUsername: ${username}\nEmail: ${email}\nPassword: ${password}`
    );

    // In a real implementation, you would redirect after successful signup
    // window.location.href = '/dashboard';
  });
});
