from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, BooleanField
from app.config import Config
from .models import User, db, PasswordResetToken
from datetime import datetime, timedelta
import random
import string
from flask_mail import Message
from . import mail

# Create authentication blueprint
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# Form classes
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
        validators.InputRequired(message="Username is required"),
        validators.Length(min=4, max=25, message="Username must be 4-25 characters")
    ])
    email = StringField('Email', validators=[
        validators.InputRequired(message="Email is required"),
        validators.Email(message="Invalid email address")
    ])
    password = PasswordField('Password', validators=[
        validators.InputRequired(message="Password is required"),
        validators.Length(min=8, message="Password must be at least 8 characters"),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        validators.InputRequired(message="Email is required"),
        validators.Email(message="Invalid email address")
    ])
    password = PasswordField('Password', validators=[
        validators.InputRequired(message="Password is required")
    ])
    remember = BooleanField('Remember Me')

# Login Route
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(Email=form.email.data).first()
        
        if not user:
            flash('No account found with this email', 'error')
            return render_template('auth/login.html', form=form)
        
        if not user.check_password(form.password.data):
            flash('Incorrect password', 'error')
            # Add error to password field
            form.password.errors.append("Incorrect password")
            return render_template('auth/login.html', form=form)
        
        login_user(user, remember=form.remember.data)
        flash('Login successful!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.upload'))
    
    # Show form errors if any
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                if field == 'password':
                    flash('Invalid login credentials', 'error')
                else:
                    flash(error, 'error')
    
    return render_template('auth/login.html', form=form)
# Signup Route
@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            if User.query.filter_by(Email=form.email.data).first():
                flash('Email already registered', 'error')
                return redirect(url_for('auth.signup'))
            
            new_user = User(
                Username=form.username.data,
                Email=form.email.data
            )
            new_user.set_password(form.password.data)
            
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
    return render_template('auth/signup.html', form=form)

# Forgot Password Form
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        validators.InputRequired(message="Email is required"),
        validators.Email(message="Invalid email address")
    ])

# Forgot Password Route
@auth_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
        else:
            email = request.form.get('email')

        user = User.query.filter_by(Email=email).first()
        if not user:
            return jsonify({'success': False, 'error': 'No account found'}), 400

        # Generate and save token
        code = ''.join(random.choices(string.digits, k=6))
        expiration = datetime.utcnow() + timedelta(minutes=15)
        
        token = PasswordResetToken.query.filter_by(user_id=user.UserID, used=False).first()
        if token:
            token.token = code
            token.expiration = expiration
        else:
            token = PasswordResetToken(
                user_id=user.UserID,
                token=code,
                expiration=expiration
            )
            db.session.add(token)
        
        db.session.commit()

        # Send email
        if not send_verification_email(user.Email, code):
            raise Exception("Email sending failed")

        return jsonify({
            'success': True,
            'email': user.Email,
            'message': 'Verification code sent'
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Password reset error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Verification Code Route
@auth_blueprint.route('/verify-code', methods=['POST'])
def verify_code():
    try:
        # Get data from JSON if AJAX, or form data if normal POST
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            code = data.get('code')
        else:
            email = request.form.get('email')
            code = request.form.get('code')

        if not email or not code:
            return jsonify({
                'success': False, 
                'error': 'Email and verification code are required'
            }), 400

        # Find user
        user = User.query.filter_by(Email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'No user found with this email'
            }), 404

        # Find valid, unused token
        token = PasswordResetToken.query.filter_by(
            user_id=user.UserID,
            token=code,
            used=False
        ).first()

        if not token:
            return jsonify({
                'success': False,
                'error': 'Invalid verification code'
            }), 400

        # Check expiration
        if token.expiration < datetime.utcnow():
            return jsonify({
                'success': False,
                'error': 'Verification code has expired'
            }), 400

        # If we get here, verification is successful
        return jsonify({
            'success': True,
            'message': 'Code verified successfully',
            'email': email,
            'code': code  # Return code for the next step
        })

    except Exception as e:
        logging.error(f"Verification error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred during verification'
        }), 500

# Reset Password Route
@auth_blueprint.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        # Get data from JSON if AJAX, or form data if normal POST
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            code = data.get('code')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
        else:
            email = request.form.get('email')
            code = request.form.get('code')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

        # Validate inputs
        if not all([email, code, password, confirm_password]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400

        if password != confirm_password:
            return jsonify({
                'success': False,
                'error': 'Passwords do not match'
            }), 400

        if len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters'
            }), 400

        # Verify user and token
        user = User.query.filter_by(Email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid user'
            }), 404

        token = PasswordResetToken.query.filter_by(
            user_id=user.UserID,
            token=code,
            used=False
        ).first()

        if not token or token.expiration < datetime.utcnow():
            return jsonify({
                'success': False,
                'error': 'Invalid or expired verification code'
            }), 400

        # Update password and mark token as used
        user.set_password(password)
        token.used = True
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Password updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Password reset error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to reset password'
        }), 500
# Send verification email function
def send_verification_email(to_email, code):
    try:
        msg = Message(
            'Password Reset Verification Code - Ecommerce InsightPro',
            sender=('Ecommerce InsightPro', Config.MAIL_USERNAME),  # More professional sender format
            recipients=[to_email]
        )
        msg.body = f'''Hello,

You requested a password reset for your Ecommerce InsightPro account.

Your verification code is: {code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email or contact support.

Thanks,
The Ecommerce InsightPro Team
'''
        # Add HTML version for better email clients
        msg.html = f'''
        <p>Hello,</p>
        <p>You requested a password reset for your Ecommerce InsightPro account.</p>
        <p><strong>Your verification code is: {code}</strong></p>
        <p>This code will expire in 15 minutes.</p>
        <p>If you didn't request this, please ignore this email or contact support.</p>
        <p>Thanks,<br>The Ecommerce InsightPro Team</p>
        '''
        
        mail.send(msg)
        logging.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
        return False
    
# Logout Route
@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.home'))
