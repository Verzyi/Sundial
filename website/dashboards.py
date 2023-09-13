from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask_bcrypt import Bcrypt
from . import db
from .mpd_dash import mpd_dash

# Create a Blueprint for your views
dashboards_bp = Blueprint('dashboards_bp', __name__)
bcrypt = Bcrypt()


@dashboards_bp.route('/printers')
@login_required
def PrinterDash():
    return render_template('dashboards/printers.html', user=current_user)


@dashboards_bp.route('/material-properties')
@login_required
def MaterialPropertiesDash():
    return render_template('dashboards/material-properties.html', dash_url=mpd_dash.url_base, user=current_user)

# @dashboards_bp.route('/material-properties')
# @login_required
# def MaterialPropertiesDash():
#     return render_template('dashboards/material_data_nb.html', user=current_user)