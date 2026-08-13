from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_babel import _
from app import db
from app.models.user import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(_('Welcome back, %(name)s!', name=user.name), 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash(_('Invalid email or password.'), 'danger')
            return render_template('login.html', view='login')

    return render_template('login.html', view='login')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash(_('All fields are required.'), 'danger')
            return render_template('login.html', view='signup')

        if password != confirm_password:
            flash(_('Passwords do not match.'), 'danger')
            return render_template('login.html', view='signup')

        if len(password) < 6:
            flash(_('Password must be at least 6 characters.'), 'danger')
            return render_template('login.html', view='signup')

        if User.query.filter_by(email=email).first():
            flash(_('Email already registered.'), 'danger')
            return render_template('login.html', view='signup')

        user = User(name=name, email=email, role='user', active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash(_('Account created successfully. Please log in.'), 'success')
        return redirect(url_for('auth.login'))

    return render_template('login.html', view='signup')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'), 'info')
    return redirect(url_for('auth.login'))
