import os
import io
import csv
from flask import Flask, redirect, url_for, flash, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuCategory
from flask_admin.actions import action 
import datetime as dt

from .mpd_dash import mpd_dash

db = SQLAlchemy()
DB_NAME = 'database.db'

def CreateDatabase(app):
    if not os.path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Database Created!')

def CreateApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jflkdsjfalksjfdsa jfsdlkjfdsljfa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Debug Toolbar Configuration
    app.config['DEBUG_TB_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    from .auth import auth
    from .views import views
    from .powder import powder
    from .builds import builds
    from .quote import quote
    from .dashboards import dashboards_bp

    bp_list = [auth, views, builds, quote]
    
    for bp in bp_list:
        app.register_blueprint(bp, url_prefix='/')
    
    app.register_blueprint(powder, url_prefix='/powder')
    app.register_blueprint(dashboards_bp, url_prefix='/dashboards')
    
    from .models import Users, PowderBlends, MaterialAlloys, MaterialProducts, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
    CreateDatabase(app)
    
    # Login info
    login_manager = LoginManager()
    login_manager.login_view = 'auth.Login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

   # Custom AdminIndexView to restrict access
    class RestrictedAdminIndexView(AdminIndexView):
        def is_accessible(self):
            if current_user.is_authenticated: 
                if (current_user.id == 1 or current_user.role == 'Admin'):
                    return current_user.is_authenticated and current_user.id == 1 or current_user.role == 'Admin' 

        def inaccessible_callback(self, name, **kwargs):
            if not current_user.is_authenticated or current_user.id != 1 or current_user.role != 'Admin':
                flash('Access denied.', category='error')
                return redirect(url_for('views.Home'))

            if request.path.startswith(self.admin.url):
                return super().inaccessible_callback(name, **kwargs)
            else:
                return redirect(url_for('views.Home'))

        def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                return self.inaccessible_callback(name, **kwargs)

            return super()._handle_view(name, **kwargs)

    admin = Admin(app, name='My Admin Panel', template_mode='bootstrap4', index_view=RestrictedAdminIndexView())

    # Create the drop-down menu categories
    users_category = MenuCategory(name='Users')
    powder_category = MenuCategory(name='Powder')
    builds_category = MenuCategory(name='Build')

    category_list = [users_category, powder_category, builds_category]
    
    for category in category_list:
        admin.add_category(category)

    # Users
    class UsersAdminView(ModelView):
        column_searchable_list = ['email', 'first_name', 'last_name', 'role']

        def is_accessible(self):
            if current_user.is_authenticated:
                return current_user.id == 1 or current_user.role == 'Admin'
            else:
                return False
        # Define a custom action to download the table as a CSV file
        @action('download_csv', 'Download CSV', 'Download selected records as CSV')
        def download_csv(self, ids):
            if not ids:
                flash('No records selected.', 'error')
                return redirect(request.referrer)

            # Get the selected records from the database
            records = self.model.query.filter(self.model.id.in_(ids)).all()

            # Create a CSV file
            output = io.StringIO()
            csv_writer = csv.writer(output)

            # Write header row
            header = ['id', 'email', 'password', 'first_name', 'last_name', 'role']  # Replace with your actual column names
            csv_writer.writerow(header)

            # Write data rows
            for record in records:
                data_row = [record.id, record.email, record.password, record.first_name, record.last_name, record.role]  
                csv_writer.writerow(data_row)

            # Prepare the response with CSV content
            response = Response(output.getvalue(), content_type='text/csv')
            timestamp = str(dt.datetime.now())[:10].replace(' ', '_').replace(':', '-').replace('-', '')
            response.headers['Content-Disposition'] = f'attachment; filename=Users_{timestamp}.csv'
            return response
    admin.add_view(UsersAdminView(Users, db.session, category=users_category.name))

    # Blend
    class BlendAdminView(ModelView):
        column_display_pk = True
        column_searchable_list = ['BlendID', 'BlendDate', 'BlendCreatedBy']
        def is_accessible(self):
            if current_user.is_authenticated:
                return current_user.id == 1 or current_user.role == 'Admin'
            else:
                return False
    admin.add_view(BlendAdminView(PowderBlends, db.session, category=powder_category.name))

    # Batch
    class BatchAdminView(ModelView):
        column_display_pk = True
        column_searchable_list = ['BatchID', 'ProductID', 'BatchCreatedBy']
        def is_accessible(self):
            if current_user.is_authenticated:
                return current_user.id == 1 or current_user.role == 'Admin'
            else:
                return False
    admin.add_view(BatchAdminView(InventoryVirginBatch, db.session, category=powder_category.name))

    # Build
    class BuildsAdminView(ModelView):
        column_display_pk = True
        def is_accessible(self):
            if current_user.is_authenticated:
                return current_user.id == 1 or current_user.role == 'Admin'
            else:
                return False
    admin.add_view(BuildsAdminView(BuildsTable, db.session, category=builds_category.name))
    
    admin.add_view(ModelView(MaterialAlloys, db.session, category=powder_category.name))
    admin.add_view(ModelView(MaterialProducts, db.session, category=powder_category.name))
    admin.add_view(ModelView(PowderBlendParts, db.session, category=powder_category.name))
    admin.add_view(ModelView(PowderBlendCalc, db.session, category=powder_category.name))

    # Initialize Dash app
    app = mpd_dash.InitDashboard(app)

    return app