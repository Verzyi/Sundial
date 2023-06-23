from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func, join
import socket
from datetime import datetime

builds = Blueprint('builds', __name__)

@builds.route('/')
@login_required
def builds_home():
    blends = PowderBlends.query.all()
    return render_template("home.html", user=current_user, blends=blends)

@builds.route('/builds', methods=['GET', 'POST'])
@login_required
def builds_page():
    if request.method == 'GET':
        builds = BuildsTable.query.all()
        # Format the 'Created On' dates
        # formatted_builds = [(build.BuildIt, build.CreatedBy, build.CreatedOn.strftime("%m/%d/%Y %H:%M")) for build in builds]

        return render_template('builds.html', user=current_user, current_build=None)

    # # Handle POST request
    # if request.method == 'POST':
    #     # Retrieve form data
    #     build_id = request.form.get('build_id')
    #     created_by = request.form.get('created_by')
    #     # Retrieve other form data

    #     # Create a new Build object and save it to the database
    #     new_build = BuildsTable(build_id=build_id, created_by=created_by)
    #     db.session.add(new_build)
    #     db.session.commit()

        # Redirect to the builds page or display a success message
    # return render_template('builds.html', user=current_user, current_build=None)
    return render_template('builds.html', user=current_user, current_build=None)
