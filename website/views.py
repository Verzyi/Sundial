from flask import Blueprint, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuCategory

from .models import Users, PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db

# Create a Blueprint for your views
views = Blueprint('views', __name__)

# # Create the admin instance
# admin = Admin(name='My Admin Panel', template_mode='bootstrap4')

# # Define the admin views

# # Users
# class UsersAdminView(ModelView):
#     column_searchable_list = ['email', 'first_name', 'last_name']

# admin.add_view(UsersAdminView(Users, db.session))

# # Blends
# class BlendModelView(ModelView):
#     column_searchable_list = ['BlendID', 'BlendDate', 'BlendCreatedBy']

# admin.add_view(BlendModelView(PowderBlends, db.session))
# admin.add_view(ModelView(MaterialsTable, db.session))
# admin.add_view(ModelView(InventoryVirginBatch, db.session))
# admin.add_view(ModelView(PowderBlendParts, db.session))
# admin.add_view(ModelView(PowderBlendCalc, db.session))

# # Builds
# admin.add_view(ModelView(BuildsTable, db.session))

# # Create the drop-down menu categories
# blends_category = MenuCategory(name='Blends')
# admin.add_category(blends_category)

# # Route for the admin panel and its sub-paths
# @views.route('/admin', defaults={'path': ''})
# @views.route('/admin/<path:path>')
# @login_required
# def admin_panel(path):
#     if current_user.is_authenticated and current_user.id == 1:
#         flash("Admin Login " + str(current_user.id), category='success')
#         return admin.index()
#     else:
#         flash("Restricted access " + str(current_user.id), category='error')
#         return redirect(url_for('blends.home'))

# # Register the admin instance to the views blueprint
# admin.init_app(views)
