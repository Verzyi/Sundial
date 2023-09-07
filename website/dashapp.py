"""Routes for parent Flask app."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, current_user
from .dashboard import dashboard

import dash
from dash import dash_table, dcc, html

dashapp_bp = Blueprint('dashapp_bp', __name__)

@dashapp_bp.route('/dashapp')
@login_required
def dashboard_template():
    return render_template('dashapp.html', dash_url=dashboard.url_base, user=current_user)