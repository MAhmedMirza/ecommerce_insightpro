from flask import Flask, render_template_string, request, redirect, url_for, session
import threading
import webbrowser
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Generate a random 6-digit verification code
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        session['reset_email'] = request.form['email']
        session['verification_code'] = generate_verification_code()
        print(f"Verification code for {session['reset_email']}: {session['verification_code']}")  # For demo only
        return redirect(url_for('verify_code'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password | E-Commerce InsightPro</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --primary-dark: #3a0ca3;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --success: #4bb543;
            --error: #ff3333;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
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
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .reset-container {
            width: 100%;
            max-width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
            animation: fadeInUp 0.5s ease-out;
        }

        .reset-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 1.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .reset-header::after {
            content: '';
            position: absolute;
            bottom: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .instruction-text {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .reset-form {
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

        .reset-btn {
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

        .reset-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .reset-btn::after {
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

        .reset-btn:hover::after {
            opacity: 1;
        }

        .back-to-login {
            text-align: center;
            font-size: 0.85rem;
            color: var(--gray);
            margin-top: 1rem;
        }

        .back-to-login a {
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

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
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

        .resend-code {
            text-align: center;
            font-size: 0.85rem;
            color: var(--gray);
            margin-top: 1rem;
        }

        .resend-code a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }

        @media (max-width: 480px) {
            .reset-container {
                max-width: 100%;
            }
            
            .reset-header {
                padding: 1.2rem;
            }
            
            .reset-form {
                padding: 1.2rem;
            }
            
            .code-input {
                width: 40px;
                height: 50px;
            }
        }
    </style>
</head>
<body>
    <div class="reset-container">
        <div class="reset-header">
            <div class="logo">Reset Password</div>
            <div class="instruction-text">Enter your email to receive a verification code</div>
        </div>
        
        <div class="reset-form">
            <form method="POST" action="/forgot-password">
                <div class="form-group">
                    <div class="input-with-icon">
                        <input type="email" id="email" name="email" class="form-control" placeholder="Email address" required>
                        <i class="fas fa-envelope"></i>
                    </div>
                </div>
                
                <button type="submit" class="reset-btn">Send Verification Code</button>
                
                <div class="back-to-login">
                    Remember your password? <a href="/login">Log in</a>
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
            const header = document.querySelector('.reset-header');
            if (header) {
                header.style.animation = 'float 6s ease-in-out infinite';
            }
        });
    </script>
</body>
</html>
    """)

@app.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        user_code = ''.join([request.form[f'code{i}'] for i in range(1, 7)])
        if user_code == session['verification_code']:
            return redirect(url_for('new_password'))
        else:
            return render_template_string("""
            <script>
                alert("Invalid verification code. Please try again.");
                window.location.href = "/verify-code";
            </script>
            """)
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Code | E-Commerce InsightPro</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Same CSS as forgot-password page */
        :root {
            --primary: #4361ee;
            --primary-dark: #3a0ca3;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --success: #4bb543;
            --error: #ff3333;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
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
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .verify-container {
            width: 100%;
            max-width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
            animation: fadeInUp 0.5s ease-out;
        }

        .verify-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 1.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .verify-header::after {
            content: '';
            position: absolute;
            bottom: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .instruction-text {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .verify-form {
            padding: 1.5rem;
        }

        .sent-to {
            text-align: center;
            font-size: 0.9rem;
            color: var(--gray);
            margin-bottom: 1rem;
        }

        .sent-to strong {
            color: var(--dark);
        }

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
            animation: pulse 1.5s infinite;
        }

        .verify-btn {
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

        .verify-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .verify-btn::after {
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

        .verify-btn:hover::after {
            opacity: 1;
        }

        .resend-code {
            text-align: center;
            font-size: 0.85rem;
            color: var(--gray);
            margin-top: 1rem;
        }

        .resend-code a {
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
            .verify-container {
                max-width: 100%;
            }
            
            .verify-header {
                padding: 1.2rem;
            }
            
            .verify-form {
                padding: 1.2rem;
            }
            
            .code-input {
                width: 40px;
                height: 50px;
            }
        }
    </style>
</head>
<body>
    <div class="verify-container">
        <div class="verify-header">
            <div class="logo">Verify Your Email</div>
            <div class="instruction-text">Enter the 6-digit code sent to your email</div>
        </div>
        
        <div class="verify-form">
            <form method="POST" action="/verify-code">
                <div class="sent-to">
                    Sent to <strong>{{ session['reset_email'] }}</strong>
                </div>
                
                <div class="code-inputs">
                    <input type="text" name="code1" class="code-input" maxlength="1" pattern="\d" required>
                    <input type="text" name="code2" class="code-input" maxlength="1" pattern="\d" required>
                    <input type="text" name="code3" class="code-input" maxlength="1" pattern="\d" required>
                    <input type="text" name="code4" class="code-input" maxlength="1" pattern="\d" required>
                    <input type="text" name="code5" class="code-input" maxlength="1" pattern="\d" required>
                    <input type="text" name="code6" class="code-input" maxlength="1" pattern="\d" required>
                </div>
                
                <button type="submit" class="verify-btn">Verify Code</button>
                
                <div class="resend-code">
                    Didn't receive a code? <a href="#" id="resendLink">Resend code</a>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Auto-focus next input when a digit is entered
        document.addEventListener('DOMContentLoaded', function() {
            const inputs = document.querySelectorAll('.code-input');
            
            inputs.forEach((input, index) => {
                // Focus first input on load
                if (index === 0) input.focus();
                
                // Move to next input on digit entry
                input.addEventListener('input', function() {
                    if (this.value.length === 1 && index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    }
                });
                
                // Handle backspace to move to previous input
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Backspace' && this.value.length === 0 && index > 0) {
                        inputs[index - 1].focus();
                    }
                });
                
                // Add pulse animation on focus
                input.addEventListener('focus', function() {
                    this.style.animation = 'pulse 1.5s infinite';
                });
                
                input.addEventListener('blur', function() {
                    this.style.animation = 'none';
                });
            });
            
            // Floating animation for header circle
            const header = document.querySelector('.verify-header');
            if (header) {
                header.style.animation = 'float 6s ease-in-out infinite';
            }
            
            // Resend code link
            const resendLink = document.getElementById('resendLink');
            if (resendLink) {
                resendLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    alert('A new verification code has been sent to your email!');
                    // In a real app, you would resend the code here
                });
            }
        });
    </script>
</body>
</html>
    """, session=session)

@app.route('/new-password', methods=['GET', 'POST'])
def new_password():
    if 'reset_email' not in session or 'verification_code' not in session:
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template_string("""
            <script>
                alert("Passwords don't match. Please try again.");
                window.location.href = "/new-password";
            </script>
            """)
        
        # In a real app, you would update the password in the database here
        session.pop('reset_email', None)
        session.pop('verification_code', None)
        return redirect(url_for('login'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Password | E-Commerce InsightPro</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Same CSS as previous pages */
        :root {
            --primary: #4361ee;
            --primary-dark: #3a0ca3;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --success: #4bb543;
            --error: #ff3333;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
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
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .password-container {
            width: 100%;
            max-width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
            animation: fadeInUp 0.5s ease-out;
        }

        .password-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 1.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .password-header::after {
            content: '';
            position: absolute;
            bottom: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .instruction-text {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .password-form {
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

        .password-btn {
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

        .password-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .password-btn::after {
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

        .password-btn:hover::after {
            opacity: 1;
        }

        /* Password strength indicator */
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
            .password-container {
                max-width: 100%;
            }
            
            .password-header {
                padding: 1.2rem;
            }
            
            .password-form {
                padding: 1.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="password-container">
        <div class="password-header">
            <div class="logo">Create New Password</div>
            <div class="instruction-text">Enter and confirm your new password</div>
        </div>
        
        <div class="password-form">
            <form method="POST" action="/new-password">
                <div class="form-group">
                    <div class="input-with-icon">
                        <input type="password" id="password" name="password" class="form-control" placeholder="New password" required>
                        <i class="fas fa-lock"></i>
                    </div>
                    <div class="password-strength">
                        <div class="strength-bar" id="strengthBar"></div>
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="input-with-icon">
                        <input type="password" id="confirm_password" name="confirm_password" class="form-control" placeholder="Confirm password" required>
                        <i class="fas fa-lock"></i>
                    </div>
                </div>
                
                <button type="submit" class="password-btn">Reset Password</button>
            </form>
        </div>
    </div>

    <script>
        // Password strength indicator
        const passwordInput = document.getElementById('password');
        const strengthBar = document.getElementById('strengthBar');
        
        passwordInput.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updateStrengthBar(strength);
        });
        
        function calculatePasswordStrength(password) {
            let strength = 0;
            
            // Length check
            if (password.length >= 8) strength += 1;
            if (password.length >= 12) strength += 1;
            
            // Character variety checks
            if (/[A-Z]/.test(password)) strength += 1;
            if (/[0-9]/.test(password)) strength += 1;
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;
            
            return Math.min(strength, 5); // Max strength of 5
        }
        
        function updateStrengthBar(strength) {
            const colors = ['#ff3333', '#ff6b6b', '#feca57', '#1dd1a1', '#4bb543'];
            const width = strength * 20;
            
            strengthBar.style.width = `${width}%`;
            strengthBar.style.background = colors[strength - 1] || colors[0];
        }
        
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
            const header = document.querySelector('.password-header');
            if (header) {
                header.style.animation = 'float 6s ease-in-out infinite';
            }
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
    app.run(debug=False, port=5000)

threading.Thread(target=run_app).start()
webbrowser.open("http://127.0.0.1:5000/forgot-password")