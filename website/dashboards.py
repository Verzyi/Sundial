from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask_bcrypt import Bcrypt
from . import db

# Create a Blueprint for your views
dashboards_bp = Blueprint('dashboards_bp', __name__)
bcrypt = Bcrypt()


@dashboards_bp.route('/printers')
@login_required
def PrinterDash():
    return render_template('dashboards/printers.html', user=current_user)