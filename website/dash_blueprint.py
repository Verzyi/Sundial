# dash_blueprint.py
from flask import Blueprint, render_template
from .dash_app import app
from flask_login import login_required, current_user

dash_blueprint = Blueprint('dash', __name__)

@dash_blueprint.route('/dash/')
@login_required
def dash_view():
    return render_template('dash_template.html', user=current_user)
