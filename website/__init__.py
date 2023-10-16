import os
import io
import csv
from flask import Flask, redirect, url_for, flash, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuCategory
from flask_admin.actions import action 
import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler
from .machine_dashboard import machine_dashboard
from .machine_dashboard import dashboard  # Import the dashboard function
from flask_migrate import Migrate
from .mpd_dash import mpd_dash



db = SQLAlchemy()
DB_NAME = 'database.db'
DB_STATUS_NAME = 'dmls_status.db'

def CreateDatabase(app):
    if not os.path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Database Created!')
            
def CreateStatusDatabase(app):
    if not os.path.exists('instance/' + DB_STATUS_NAME):
        with app.app_context():
            db.create_all()
            print('Status Database Created!')
            
def Createscheduler(app):
    # Create a scheduler instance
    scheduler = BackgroundScheduler()

    # Schedule the dashboard function to run every 5 minutes
    scheduler.add_job(lambda: dashboard(app), 'interval', minutes=5, id='dashboard_job')

    # Start the scheduler within the Flask app context
    with app.app_context():
        print("printer dash turned off")
        # scheduler.start()


def CreateApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jflkdsjfalksjfdsa jfsdlkjfdsljfa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_BINDS'] = {
        'dmls_status': f'sqlite:///{DB_STATUS_NAME}',  # Bind the 'dmls_status' database
        'main': f'sqlite:///{DB_NAME}'  # Bind the main database (you can change 'main' to your preferred name)
    }
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    migrate = Migrate(app, db)
    
    
    
    # Debug Toolbar Configuration
    app.config['DEBUG_TB_ENABLED'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    from .auth import auth
    from .views import views
    from .powder import powder
    from .builds import builds
    from .quote import quote
    from .dashboards import dashboards_bp
    from .scheduler import scheduler
    from .migrate import migrate_bp
    # from .maintenance import maintenance_bp

    bp_list = [auth, views, machine_dashboard, quote, scheduler]
    
    for bp in bp_list:
        app.register_blueprint(bp, url_prefix='/')
    
    app.register_blueprint(builds, url_prefix='/builds')
    app.register_blueprint(powder, url_prefix='/powder')
    app.register_blueprint(dashboards_bp, url_prefix='/dashboards')
    app.register_blueprint(migrate_bp, url_prefix='/migrate')


    from .models_status import StatusTable
    from .models import Users, PowderBlends, MaterialAlloys, MaterialProducts, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable 
    from .models import TaskTypes, Tasks, ScheduleTasks, Machines, Location
    # Create the main database
    CreateStatusDatabase(app)
    CreateDatabase(app)
    
    Createscheduler(app)





    
    
    
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
    fix_category = MenuCategory(name='Fix-tools')

    category_list = [users_category, powder_category, builds_category, fix_category]
    
    for category in category_list:
        admin.add_category(category)

    # Users
    class UsersAdminView(ModelView):
        column_display_pk = True
        column_searchable_list = ['id', 'email', 'first_name', 'last_name', 'role']
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
    admin.add_view(BlendAdminView(PowderBlends, db.session, category=powder_category.name))

    # Batch
    class BatchAdminView(ModelView):
        column_display_pk = True
        column_searchable_list = ['BatchID', 'ProductID', 'BatchCreatedBy']
    admin.add_view(BatchAdminView(InventoryVirginBatch, db.session, category=powder_category.name))
    
    # PowderBlendParts
    class BlendPartsAdminView(ModelView):
        column_display_pk = True
        column_searchable_list = ['PartID', 'BlendID']
    admin.add_view(BlendPartsAdminView(PowderBlendParts, db.session, category=powder_category.name))
    
    # PowderBlendCalc
    class BlendCalcAdminView(ModelView):
        column_display_pk = True
        column_searchable_list = ['BlendID']
    admin.add_view(BlendCalcAdminView(PowderBlendCalc, db.session, category=powder_category.name))

    # Build
    class BuildsAdminView(ModelView):
        column_display_pk = True
        column_searchable_list = ['BuildID']
    admin.add_view(BuildsAdminView(BuildsTable, db.session, category=builds_category.name))
    
    admin.add_view(ModelView(MaterialAlloys, db.session, category=powder_category.name))
    admin.add_view(ModelView(MaterialProducts, db.session, category=powder_category.name))
    
    class FixToolView(AdminIndexView):
        # column_display_pk = True
        column_searchable_list = ['BlendID']
        
        

        def get_list(self, page, sort_column, sort_desc, search, filters, page_size=None):
            # Call the parent get_list method if a search query is present
            if search is not None and search.strip() != '':
                return super().get_list(page, sort_column, sort_desc, search, filters, page_size)

            # Get all records from the database
            count, data = self.get_list_page(0, None, None, None, None)

            # Return all records if no search query is present
            return data, count, {}
        
        def fixtool():
            @expose('/fix-tool/')
            def index(self):
                return self.render_template('admin/fix_tool.html')  
    
        
    @expose('/')
    def index(self):
        return self.render_template('admin/index.html')
    
    
      

    # Add the FixToolView to the admin panel
    admin.add_view(FixToolView(name='Fix Tool', endpoint='fix-tool', category=powder_category.name, url='/fix-tool/' , menu_icon_type='glyph', menu_icon_value='glyphicon-wrench'))



    # Initialize Dash app
    app = mpd_dash.InitDashboard(app)

    return app