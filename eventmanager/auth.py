from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
from .forms import LoginForm, RegisterForm

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            first_name=form.first_name.data,
            surname=form.surname.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            phone=form.phone.data or None,
            address=form.address.data or None
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('views.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('views.index'))
