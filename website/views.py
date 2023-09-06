from flask import Blueprint, redirect, url_for, flash,render_template,request
from flask_login import current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuCategory
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Users, PowderBlends, MaterialProducts, MaterialAlloys, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from flask_bcrypt import Bcrypt, check_password_hash 
from . import db

# Create a Blueprint for your views
views = Blueprint('views', __name__)
bcrypt = Bcrypt()

@views.route('/')
@login_required
def builds_home():
    blends = PowderBlends.query.all()
    return render_template('home.html', user=current_user)


@views.route('/Settings', methods=['GET', 'POST'])
@login_required
def Settings():
    if request.method == 'POST':
        # Get the form input values
        new_password1 = request.form.get('new_password1')
        new_password2 = request.form.get('new_password2')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        # Check if the user wants to update their password
        if new_password1 is not None:
            if new_password1 != new_password2:
                flash('New passwords don\'t match', category='error')
            elif len(new_password1) < 6:
                flash('New password must be at least 6 characters long', category='error')
            else:
                # Update the user's password
                hashed_password = bcrypt.generate_password_hash(new_password1).decode('utf-8')
                current_user.password = hashed_password
                db.session.commit()
                flash('Password updated successfully', category='success')

        # Update the user's first name and last name
        current_user.first_name = first_name
        current_user.last_name = last_name
        db.session.commit()

        flash('Account updated', category='success')

    return render_template("Settings.html", user=current_user)
