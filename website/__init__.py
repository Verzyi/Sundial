from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuCategory, MenuLink

db = SQLAlchemy()
DB_NAME = "database.db"

def create_database(app):
    if not os.path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
            print("Database Created!")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jflkdsjfalksjfdsa jfsdlkjfdsljfa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    admin = Admin(app, name='My Admin Panel', template_mode='bootstrap4')

    # Debug Toolbar Configuration
    app.config['DEBUG_TB_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    from .blends import blends
    from .auth import auth
    from .builds import builds
    from .views import views

    app.register_blueprint(blends, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(builds, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    from .models import Users, PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable

    create_database(app)
    
    # Login info
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    # Custom AdminIndexView to restrict access
    class RestrictedAdminIndexView(AdminIndexView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.id == 1

        def inaccessible_callback(self, name, **kwargs):
            flash("Access denied.", category='error')
            return redirect(url_for('blends.home'))

    admin.index_view = RestrictedAdminIndexView()

    # Admin info
    # Create the drop-down menu category
    class CustomCategory(MenuCategory):
        def __str__(self):
            return self.name

    # Create the dropdown menu categories
    users_category = CustomCategory(name='Users')
    blends_category = CustomCategory(name='Blend')
    builds_category = CustomCategory(name='Build')

    # Add the categories to the admin menu
    admin.add_category(users_category)
    admin.add_category(blends_category)
    admin.add_category(builds_category)

    # Register your existing views under the corresponding categories
    # Users
    class UsersAdminView(ModelView):
        column_searchable_list = ['email', 'first_name', 'last_name']

    admin.add_view(UsersAdminView(Users, db.session, category=users_category.name))

    # Blend
    class BlendModelView(ModelView):
        column_searchable_list = ['BlendID', 'BlendDate', 'BlendCreatedBy']

    admin.add_view(BlendModelView(PowderBlends, db.session, category=blends_category.name))
    admin.add_view(ModelView(MaterialsTable, db.session, category=blends_category.name))
    admin.add_view(ModelView(InventoryVirginBatch, db.session, category=blends_category.name))
    admin.add_view(ModelView(PowderBlendParts, db.session, category=blends_category.name))
    admin.add_view(ModelView(PowderBlendCalc, db.session, category=blends_category.name))

    # Build
    admin.add_view(ModelView(BuildsTable, db.session, category=builds_category.name))

    return app
