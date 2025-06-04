// Scroll animations
document.addEventListener("DOMContentLoaded", function () {
  const animateOnScroll = () => {
    const elements = document.querySelectorAll(
      ".solution, .goal, .signup-login, .footer-content"
    );

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = 1;
            entry.target.style.transform = "translateY(0)";
          }
        });
      },
      { threshold: 0.1 }
    );

    elements.forEach((el) => {
      el.style.opacity = 0;
      el.style.transform = "translateY(20px)";
      el.style.transition = "all 0.6s ease-out";
      observer.observe(el);
    });
  };

  // Run the animation function
  animateOnScroll();

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });
});

// Floating animation for header image
const headerImage = document.querySelector(".header-image img");
if (headerImage) {
  headerImage.style.animation = "float 6s ease-in-out infinite";
}
