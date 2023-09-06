from flask import Blueprint, redirect, url_for, flash,render_template,request
from flask_login import current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuCategory
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Users, PowderBlends, MaterialProducts, MaterialAlloys, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db

# Create a Blueprint for your views
views = Blueprint('views', __name__)

@views.route('/')
@login_required
def builds_home():
    blends = PowderBlends.query.all()
    return render_template('home.html', user=current_user)


@views.route('/Settings', methods=['GET', 'POST'])
@login_required
def Settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password1 = request.form.get('new_password1')
        new_password2 = request.form.get('new_password2')

        # Check if the entered current password matches the user's actual password
        if not current_user.check_password(current_password):
            flash('Incorrect current password', category='error')
        elif new_password1 != new_password2:
            flash('New passwords don\'t match', category='error')
        elif len(new_password1) < 6:
            flash('New password must be at least 6 characters long', category='error')
        else:
            # Update the user's password
            current_user.set_password(new_password1)
            db.session.commit()
            flash('Password updated successfully', category='success')
            return redirect(url_for('views.Settings'))

    return render_template("Settings.html", user=current_user)