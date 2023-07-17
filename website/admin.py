from flask import Blueprint
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .models import Users, PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin = Admin(name='Admin Panel', template_mode='bootstrap3')

class UsersAdminView(ModelView):
    # Configuration for Users section
    column_list = ['email', 'first_name', 'last_name']

class BlendAdminView(ModelView):
    # Configuration for Blend section
    column_list = ['BlendID', 'BlendDate', 'BlendCreatedBy']

class BuildAdminView(ModelView):
    # Configuration for Build section
    column_list = ['BuildIt', 'CreatedOn', 'BuildName']

# Register the admin views
admin.add_view(UsersAdminView(Users, db.session, category='Users'))
admin.add_view(BlendAdminView(PowderBlends, db.session, category='Blend'))
admin.add_view(BuildAdminView(BuildsTable, db.session, category='Build'))

@admin_bp.route('/')
def index():
    return admin.index()

@admin_bp.route('/user/')
def user():
    return 'User Section'

@admin_bp.route('/blend/')
def blend():
    return 'Blend Section'

@admin_bp.route('/build/')
def build():
    return 'Build Section'

def configure_admin(app):
    admin.init_app(app)
