from flask import Flask, render_template_string, request, redirect, url_for, session
import threading
import webbrowser
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Generate verification code
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/')
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce InsightPro</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --primary-dark: #3a0ca3;
            --secondary: #4cc9f0;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f5f7ff;
            color: var(--dark);
            line-height: 1.7;
            overflow-x: hidden;
        }

        /* Home Page Content */
        .home-content {
            transition: var(--transition);
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }

        .blur-active {
            filter: blur(5px);
            pointer-events: none;
            user-select: none;
        }

        /* Auth Modal Container */
        .auth-modal-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: var(--transition);
        }

        .auth-modal-container.active {
            opacity: 1;
            visibility: visible;
        }

        /* Modal Backdrop */
        .modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1;
        }

        /* Auth Modal */
        .auth-modal {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
            transform: translateY(20px);
            transition: var(--transition);
        }

        .auth-modal-container.active .auth-modal {
            transform: translateY(0);
        }

        /* Modal Header */
        .auth-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 1.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .auth-header::after {
            content: '';
            position: absolute;
            bottom: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }

        .auth-logo {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .auth-subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        /* Auth Form */
        .auth-form {
            padding: 1.5rem;
        }

        /* Form Elements (Same as before) */
        .form-group {
            margin-bottom: 1.2rem;
            position: relative;
        }

        .input-with-icon {
            position: relative;
        }

        .input-with-icon i {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gray);
            font-size: 1rem;
            transition: var(--transition);
        }

        .form-control {
            width: 100%;
            padding: 10px 10px 10px 38px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: var(--transition);
            height: 42px;
        }

        .form-control:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
            animation: pulse 1.5s infinite;
        }

        .form-control:focus + i {
            color: var(--primary);
            transform: translateY(-50%) scale(1.1);
        }

        /* Buttons */
        .auth-btn {
            width: 100%;
            padding: 10px;
            background: linear-gradient(to right, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
            margin-top: 0.5rem;
            position: relative;
            overflow: hidden;
        }

        .auth-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .auth-btn::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to right, var(--primary-dark), var(--primary));
            opacity: 0;
            transition: var(--transition);
        }

        .auth-btn:hover::after {
            opacity: 1;
        }

        /* Close Button */
        .close-modal {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255,255,255,0.2);
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: var(--transition);
            z-index: 3;
        }

        .close-modal:hover {
            background: rgba(255,255,255,0.3);
            transform: rotate(90deg);
        }

        /* Verification Code Inputs */
        .code-inputs {
            display: flex;
            justify-content: space-between;
            margin: 1.5rem 0;
        }

        .code-input {
            width: 45px;
            height: 55px;
            text-align: center;
            font-size: 1.2rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            transition: var(--transition);
        }

        .code-input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
        }

        /* Password Strength */
        .password-strength {
            height: 4px;
            background: #e0e0e0;
            border-radius: 2px;
            margin-top: 5px;
            overflow: hidden;
        }

        .strength-bar {
            height: 100%;
            width: 0%;
            background: var(--error);
            transition: var(--transition);
        }

        /* Toggle Links */
        .auth-toggle {
            text-align: center;
            font-size: 0.85rem;
            color: var(--gray);
            margin-top: 1rem;
        }

        .auth-toggle a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }

        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0.2); }
            70% { box-shadow: 0 0 0 8px rgba(67, 97, 238, 0); }
            100% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0); }
        }

        /* Responsive */
        @media (max-width: 480px) {
            .auth-modal {
                max-width: 90%;
            }
            
            .code-input {
                width: 40px;
                height: 50px;
            }
        }
    </style>
</head>
<body>
    <!-- Home Content (Blurred when modal is open) -->
    <div class="home-content" id="homeContent">
        <header>
            <div style="padding: 20px; text-align: center;">
                <h1 style="font-size: 2.5rem; color: var(--primary);">E-Commerce InsightPro</h1>
                <p style="color: var(--gray);">Your complete e-commerce analytics solution</p>
            </div>
        </header>
        
        <main style="text-align: center; margin-top: 50px;">
            <button onclick="showAuthModal('login')" style="padding: 12px 30px; background: var(--primary); color: white; border: none; border-radius: 50px; font-size: 1rem; cursor: pointer; margin: 10px;">
                Login
            </button>
            <button onclick="showAuthModal('signup')" style="padding: 12px 30px; background: var(--primary-dark); color: white; border: none; border-radius: 50px; font-size: 1rem; cursor: pointer; margin: 10px;">
                Sign Up
            </button>
        </main>
    </div>

    <!-- Auth Modals Container -->
    <div class="auth-modal-container" id="authModalContainer">
        <div class="modal-backdrop" onclick="hideAuthModal()"></div>
        
        <!-- Login Modal -->
        <div class="auth-modal" id="loginModal">
            <div class="close-modal" onclick="hideAuthModal()">
                <i class="fas fa-times"></i>
            </div>
            <div class="auth-header">
                <div class="auth-logo">Welcome Back</div>
                <div class="auth-subtitle">Login to your account</div>
            </div>
            <div class="auth-form">
                <form id="loginForm">
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="email" id="loginEmail" class="form-control" placeholder="Email address" required>
                            <i class="fas fa-envelope"></i>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="password" id="loginPassword" class="form-control" placeholder="Password" required>
                            <i class="fas fa-lock"></i>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; margin: 1rem 0;">
                        <div>
                            <input type="checkbox" id="rememberMe">
                            <label for="rememberMe">Remember me</label>
                        </div>
                        <div>
                            <a href="#" onclick="showAuthModal('forgot')" style="color: var(--primary); text-decoration: none;">Forgot password?</a>
                        </div>
                    </div>
                    <button type="submit" class="auth-btn">Log In</button>
                    <div class="auth-toggle">
                        Don't have an account? <a href="#" onclick="showAuthModal('signup')">Sign up</a>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Signup Modal -->
        <div class="auth-modal" id="signupModal" style="display: none;">
            <div class="close-modal" onclick="hideAuthModal()">
                <i class="fas fa-times"></i>
            </div>
            <div class="auth-header">
                <div class="auth-logo">Create Account</div>
                <div class="auth-subtitle">Get started with InsightPro</div>
            </div>
            <div class="auth-form">
                <form id="signupForm">
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="text" id="signupUsername" class="form-control" placeholder="Username" required>
                            <i class="fas fa-user"></i>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="email" id="signupEmail" class="form-control" placeholder="Email address" required>
                            <i class="fas fa-envelope"></i>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="password" id="signupPassword" class="form-control" placeholder="Password" required>
                            <i class="fas fa-lock"></i>
                        </div>
                        <div class="password-strength">
                            <div class="strength-bar" id="signupStrengthBar"></div>
                        </div>
                    </div>
                    <button type="submit" class="auth-btn">Sign Up</button>
                    <div class="auth-toggle">
                        Already have an account? <a href="#" onclick="showAuthModal('login')">Log in</a>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Forgot Password Modal -->
        <div class="auth-modal" id="forgotModal" style="display: none;">
            <div class="close-modal" onclick="hideAuthModal()">
                <i class="fas fa-times"></i>
            </div>
            <div class="auth-header">
                <div class="auth-logo">Reset Password</div>
                <div class="auth-subtitle">Enter your email to continue</div>
            </div>
            <div class="auth-form">
                <form id="forgotForm">
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="email" id="forgotEmail" class="form-control" placeholder="Email address" required>
                            <i class="fas fa-envelope"></i>
                        </div>
                    </div>
                    <button type="submit" class="auth-btn">Send Reset Link</button>
                    <div class="auth-toggle">
                        Remember your password? <a href="#" onclick="showAuthModal('login')">Log in</a>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Verification Code Modal -->
        <div class="auth-modal" id="verifyModal" style="display: none;">
            <div class="close-modal" onclick="hideAuthModal()">
                <i class="fas fa-times"></i>
            </div>
            <div class="auth-header">
                <div class="auth-logo">Verify Email</div>
                <div class="auth-subtitle">Enter the 6-digit code</div>
            </div>
            <div class="auth-form">
                <form id="verifyForm">
                    <div style="text-align: center; font-size: 0.9rem; margin-bottom: 1rem;">
                        Sent to <strong id="verifyEmailDisplay">user@example.com</strong>
                    </div>
                    <div class="code-inputs">
                        <input type="text" maxlength="1" class="code-input" required>
                        <input type="text" maxlength="1" class="code-input" required>
                        <input type="text" maxlength="1" class="code-input" required>
                        <input type="text" maxlength="1" class="code-input" required>
                        <input type="text" maxlength="1" class="code-input" required>
                        <input type="text" maxlength="1" class="code-input" required>
                    </div>
                    <button type="submit" class="auth-btn">Verify Code</button>
                    <div class="auth-toggle">
                        Didn't receive code? <a href="#" id="resendCode">Resend</a>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- New Password Modal -->
        <div class="auth-modal" id="newPasswordModal" style="display: none;">
            <div class="close-modal" onclick="hideAuthModal()">
                <i class="fas fa-times"></i>
            </div>
            <div class="auth-header">
                <div class="auth-logo">New Password</div>
                <div class="auth-subtitle">Create your new password</div>
            </div>
            <div class="auth-form">
                <form id="newPasswordForm">
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="password" id="newPassword" class="form-control" placeholder="New password" required>
                            <i class="fas fa-lock"></i>
                        </div>
                        <div class="password-strength">
                            <div class="strength-bar" id="newPasswordStrengthBar"></div>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <input type="password" id="confirmPassword" class="form-control" placeholder="Confirm password" required>
                            <i class="fas fa-lock"></i>
                        </div>
                    </div>
                    <button type="submit" class="auth-btn">Reset Password</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        // Show auth modal
        function showAuthModal(modalType) {
            const container = document.getElementById('authModalContainer');
            const homeContent = document.getElementById('homeContent');
            
            // Hide all modals first
            document.querySelectorAll('.auth-modal').forEach(modal => {
                modal.style.display = 'none';
            });
            
            // Show selected modal
            document.getElementById(`${modalType}Modal`).style.display = 'block';
            
            // Activate modal container
            container.classList.add('active');
            homeContent.classList.add('blur-active');
            
            // Focus first input
            setTimeout(() => {
                const firstInput = document.querySelector(`#${modalType}Modal .form-control`);
                if (firstInput) firstInput.focus();
            }, 100);
        }
        
        // Hide auth modal
        function hideAuthModal() {
            const container = document.getElementById('authModalContainer');
            const homeContent = document.getElementById('homeContent');
            
            container.classList.remove('active');
            homeContent.classList.remove('blur-active');
        }
        
        // Password strength indicator
        function setupPasswordStrength(inputId, barId) {
            const input = document.getElementById(inputId);
            const bar = document.getElementById(barId);
            
            input.addEventListener('input', function() {
                const strength = calculatePasswordStrength(this.value);
                updateStrengthBar(bar, strength);
            });
        }
        
        function calculatePasswordStrength(password) {
            let strength = 0;
            
            if (password.length >= 8) strength += 1;
            if (password.length >= 12) strength += 1;
            if (/[A-Z]/.test(password)) strength += 1;
            if (/[0-9]/.test(password)) strength += 1;
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;
            
            return Math.min(strength, 5);
        }
        
        function updateStrengthBar(bar, strength) {
            const colors = ['#ff3333', '#ff6b6b', '#feca57', '#1dd1a1', '#4bb543'];
            const width = strength * 20;
            
            bar.style.width = `${width}%`;
            bar.style.background = colors[strength - 1] || colors[0];
        }
        
        // Verification code input auto-focus
        function setupCodeInputs() {
            const inputs = document.querySelectorAll('.code-input');
            
            inputs.forEach((input, index) => {
                // Focus first input
                if (index === 0) input.focus();
                
                // Move to next input on digit entry
                input.addEventListener('input', function() {
                    if (this.value.length === 1 && index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    }
                });
                
                // Handle backspace
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Backspace' && this.value.length === 0 && index > 0) {
                        inputs[index - 1].focus();
                    }
                });
            });
        }
        
        // Form submissions
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Login functionality would be implemented here');
            hideAuthModal();
        });
        
        document.getElementById('signupForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Signup functionality would be implemented here');
            hideAuthModal();
        });
        
        document.getElementById('forgotForm').addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('verifyEmailDisplay').textContent = 
                document.getElementById('forgotEmail').value;
            showAuthModal('verify');
        });
        
        document.getElementById('verifyForm').addEventListener('submit', function(e) {
            e.preventDefault();
            showAuthModal('newPassword');
        });
        
        document.getElementById('newPasswordForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const password = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                alert("Passwords don't match!");
                return;
            }
            
            alert('Password reset successful!');
            hideAuthModal();
        });
        
        // Resend code link
        document.getElementById('resendCode').addEventListener('click', function(e) {
            e.preventDefault();
            alert('New verification code sent!');
        });
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setupPasswordStrength('signupPassword', 'signupStrengthBar');
            setupPasswordStrength('newPassword', 'newPasswordStrengthBar');
            setupCodeInputs();
            
            // Floating animation for header circles
            document.querySelectorAll('.auth-header').forEach(header => {
                header.style.animation = 'float 6s ease-in-out infinite';
            });
        });
    </script>
</body>
</html>
    """)

def run_app():
    app.run(debug=False, port=5000)

threading.Thread(target=run_app).start()
webbrowser.open("http://127.0.0.1:5000/")