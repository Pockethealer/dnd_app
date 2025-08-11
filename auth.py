from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .decorators import admin_required
import re

auth = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Basic validation
        if not email or not re.match(EMAIL_REGEX, email):
            flash('Invalid email address.', category='error')
            return render_template("login.html", user=current_user)

        if not password:
            flash('Password cannot be empty.', category='error')
            return render_template("login.html", user=current_user)

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password!', category='error')
        else:
            flash('User does not exist!', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
@login_required
@admin_required
def sign_up():
    if request.method=='POST':
        email=request.form.get('email')
        name=request.form.get('Name')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email)<4:
            flash('Email must be valid', category='error')
        elif len(name)<2:
            flash('Name must be valid', category='error')
        elif password1!=password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1)<6:
            flash('Password must be at least 6 characters', category='error')
        else:
            new_user =User(email=email, name=name, password=generate_password_hash(password1), is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            flash('Success, account created!', category='success')
            return redirect(url_for('admin.admin_dashboard'))
    return render_template("sign_up.html", user=current_user)