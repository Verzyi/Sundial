from flask import Blueprint, redirect, url_for, request, render_template, request, flash, redirect, url_for, session
from flask_bcrypt import Bcrypt, check_password_hash 
from flask_login import login_user, login_required, logout_user, current_user

from . import db
from .models import Users

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt() 


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully.', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.Home'))
            else:
                flash('Password incorrect!', category='error')
        else:
            flash('Email does not exist!', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/guest-login', methods=['GET'])
def guest_login():
    # Create a guest user with a unique email
    email = 'guest_' + str(hash(request.remote_addr))
    password = 'guest_password'

    # Check if the guest user already exists
    guest_user = Users.query.filter_by(email=email).first()
    if guest_user:
        login_user(guest_user, remember=True)
        flash('Logged in as guest.', category='success')
        return redirect(url_for('views.Home'))

    # Create a new guest user
    last_user = Users.query.order_by(Users.id.desc()).first()
    last_id = last_user.id if last_user else 0
    new_id = last_id + 1

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = Users(
        id=new_id,
        email=email,
        first_name='Guest',
        last_name='',
        password=hashed_password,
        role='Guest'
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    flash('Logged in as guest.', category='success')
    return redirect(url_for('views.Home'))

    # If the guest user exists and has been deleted or any other case, render login.html
    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    session['_remember'] = 'clear'
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Users.query.filter_by(email=email).first()
        if user:
            flash('Email already exists!', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters!', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character!', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character!', category='error')
        elif password1 != password2:
            flash('Passwords do not match!', category='error')
        elif len(password1) < 6:
            flash('Password must be greater than 6 characters!', category='error')
        else:
            hashed_password = bcrypt.generate_password_hash(password1).decode('utf-8')
            # Append Users
            last_user = Users.query.order_by(Users.id.desc()).first()
            last_id = last_user.id if last_user else 0
            new_id = last_id + 1
            new_user = Users(
                id=new_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=hashed_password,
                role='User'
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created.', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.Home'))

    return render_template('signup.html', user=current_user)
