from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify  
from .models import PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func, join, desc
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
    if request.method == 'POST':
        if 'Facility' in request.form:
            selectedFacility = request.form.get("Facility")
            session['last_selected_facility'] = selectedFacility

    selectedFacility = session.get('last_selected_facility')
    builds = []
    if selectedFacility is not None:
        builds = BuildsTable.query.filter_by(FacilityName=selectedFacility).order_by(desc(BuildsTable.BuildIt)).all()
    
    # You'll need to fetch the build information from the database
    # based on the selected build ID (use the selectedBuildID variable)
    selectedBuildID = request.form.get("solidJobsBuildIDInput")
    selectedBuild = BuildsTable.query.filter_by(BuildIt=selectedBuildID).first()

    return render_template('builds.html', user=current_user, current_build=selectedBuild, buildsInfo=builds)




@builds.route('/get_build_info/<int:buildid>', methods=['GET'])
def get_build_info(buildid):
    # Assuming you have a database table named 'BuildsTable' with a column named 'BuildId'
    build = BuildsTable.query.get(buildid)
    if build:
        # Return the filtered build information as JSON
        build_data = build.to_dict()
        return jsonify(build_data)
    else:
        # If build ID is not found, return an empty response with 404 status code
        return jsonify({"error": "Build not found"}), 404
