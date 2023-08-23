from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuCategory

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
    
    # Login info
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    # Debug Toolbar Configuration
    app.config['DEBUG_TB_ENABLED'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)
    
    from .auth import auth
    from .blends import blends
    from .builds import builds
    from .views import views
    from .quote import quote

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(blends, url_prefix='/')
    app.register_blueprint(builds, url_prefix='/')
    app.register_blueprint(quote, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    from .models import Users, PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable

    create_database(app)
    
 

   # Custom AdminIndexView to restrict access
    class RestrictedAdminIndexView(AdminIndexView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.id == 1

        def inaccessible_callback(self, name, **kwargs):
            if not current_user.is_authenticated or current_user.id != 1:
                flash("Access denied.", category='error')
                return redirect(url_for('blends.home'))

            if request.path.startswith(self.admin.url):
                return super().inaccessible_callback(name, **kwargs)
            else:
                return redirect(url_for('blends.home'))

        def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                return self.inaccessible_callback(name, **kwargs)

            return super()._handle_view(name, **kwargs)

    admin = Admin(app, name='My Admin Panel', template_mode='bootstrap4', index_view=RestrictedAdminIndexView())

    # Create the drop-down menu categories
    users_category = MenuCategory(name='Users')
    blends_category = MenuCategory(name='Blend')
    builds_category = MenuCategory(name='Build')

    # Add the categories to the admin menu
    admin.add_category(users_category)
    admin.add_category(blends_category)
    admin.add_category(builds_category)

    # Users
    class RestrictedUsersAdminView(ModelView):
        column_searchable_list = ['email', 'first_name', 'last_name']

        def is_accessible(self):
            return current_user.is_authenticated and current_user.id == 1

    admin.add_view(RestrictedUsersAdminView(Users, db.session, category=users_category.name))

    # Blend
    class RestrictedBlendModelView(ModelView):
        column_searchable_list = ['BlendID', 'BlendDate', 'BlendCreatedBy']

        def is_accessible(self):
            return current_user.is_authenticated and current_user.id == 1

    admin.add_view(RestrictedBlendModelView(PowderBlends, db.session, category=blends_category.name))
    admin.add_view(ModelView(MaterialsTable, db.session, category=blends_category.name))
    admin.add_view(ModelView(InventoryVirginBatch, db.session, category=blends_category.name))
    admin.add_view(ModelView(PowderBlendParts, db.session, category=blends_category.name))
    admin.add_view(ModelView(PowderBlendCalc, db.session, category=blends_category.name))

    # Build
    class RestrictedBuildsModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.id == 1

    admin.add_view(RestrictedBuildsModelView(BuildsTable, db.session, category=builds_category.name))

    return app
