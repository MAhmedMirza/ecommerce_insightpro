from flask import Flask, render_template_string, request, redirect, url_for, session
import threading
import webbrowser

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['email'] = request.form['email']
        return redirect(url_for('dashboard'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login | E-Commerce InsightPro</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --primary-dark: #3a0ca3;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Make body cover the entire viewport with transparent blur */
        body {
            font-family: 'Poppins', sans-serif;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent black */
            backdrop-filter: blur(8px); /* Blur effect */
            z-index: 1000; /* Ensure it's above other content */
            padding: 20px;
        }

        .login-container {
            width: 100%;
            max-width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
            animation: fadeInUp 0.5s ease-out;
            position: relative;
        }

        /* Add close button */
        .close-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            z-index: 1;
        }

        .login-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 1.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .login-header::after {
            content: '';
            position: absolute;
            bottom: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }

        /* Rest of your existing styles remain the same */
        .logo {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .welcome-text {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .login-form {
            padding: 1.5rem;
        }

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

        .form-control::placeholder {
            color: #aaa;
            font-size: 0.85rem;
        }

        .remember-forgot {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 1rem 0;
            font-size: 0.85rem;
        }

        .remember-me {
            display: flex;
            align-items: center;
        }

        .remember-me input {
            margin-right: 6px;
            accent-color: var(--primary);
        }

        .forgot-password a {
            color: var(--gray);
            text-decoration: none;
            transition: var(--transition);
        }

        .forgot-password a:hover {
            color: var(--primary);
        }

        .login-btn {
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

        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .login-btn::after {
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

        .login-btn:hover::after {
            opacity: 1;
        }

        .divider {
            display: flex;
            align-items: center;
            margin: 1.2rem 0;
            color: var(--gray);
            font-size: 0.8rem;
        }

        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #e0e0e0;
        }

        .divider span {
            padding: 0 10px;
        }

        .social-login {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 1rem;
        }

        .social-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1rem;
            transition: var(--transition);
        }

        .social-btn:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-sm);
        }

        .facebook { background: #3b5998; }
        .google { background: #db4437; }
        .twitter { background: #1da1f2; }

        .signup-link {
            text-align: center;
            font-size: 0.85rem;
            color: var(--gray);
        }

        .signup-link a {
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

        @media (max-width: 480px) {
            .login-container {
                max-width: 100%;
            }
            
            .login-header {
                padding: 1.2rem;
            }
            
            .login-form {
                padding: 1.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <button class="close-btn" onclick="window.history.back()">&times;</button>
        <div class="login-header">
            <div class="logo">E-Commerce InsightPro</div>
            <div class="welcome-text">Welcome back! Please login to continue</div>
        </div>
        
        <div class="login-form">
            <form method="POST" action="/login">
                <div class="form-group">
                    <div class="input-with-icon">
                        <input type="email" id="email" name="email" class="form-control" placeholder="Email address" required>
                        <i class="fas fa-envelope"></i>
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="input-with-icon">
                        <input type="password" id="password" name="password" class="form-control" placeholder="Password" required>
                        <i class="fas fa-lock"></i>
                    </div>
                </div>
                
                <div class="remember-forgot">
                    <div class="remember-me">
                        <input type="checkbox" id="remember" name="remember">
                        <label for="remember">Remember me</label>
                    </div>
                    <div class="forgot-password">
                        <a href="/forgot-password">Forgot password?</a>
                    </div>
                </div>
                
                <button type="submit" class="login-btn">Log In</button>
                
                <div class="divider">
                    <span>or continue with</span>
                </div>
                
                <div class="social-login">
                    <a href="#" class="social-btn facebook">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="#" class="social-btn google">
                        <i class="fab fa-google"></i>
                    </a>
                    <a href="#" class="social-btn twitter">
                        <i class="fab fa-twitter"></i>
                    </a>
                </div>
                
                <div class="signup-link">
                    Don't have an account? <a href="/signup">Sign up</a>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Add focus effects to input fields
        document.addEventListener('DOMContentLoaded', function() {
            const inputs = document.querySelectorAll('.form-control');
            
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.style.animation = 'pulse 1.5s infinite';
                });
                
                input.addEventListener('blur', function() {
                    this.style.animation = 'none';
                });
            });
            
            // Floating animation for header circle
            const header = document.querySelector('.login-header');
            if (header) {
                header.style.animation = 'float 6s ease-in-out infinite';
            }

            // Close when clicking outside the login container
            document.body.addEventListener('click', function(e) {
                if (e.target === document.body) {
                    window.history.back();
                }
            });
        });
    </script>
</body>
</html>
""")
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    return "Welcome to your dashboard!"

def run_app():
    app.run(debug=False, port=5001)

if __name__ == '__main__':
    app.run(port=5000)  # Different port for login

threading.Thread(target=run_app).start()
webbrowser.open("http://127.0.0.1:5000/login")