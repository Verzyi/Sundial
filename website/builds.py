from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, Response, make_response
from .models import PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func, join, desc
import socket
from datetime import datetime
import pandas as pd
from math import ceil
import pdfkit
from pdfkit.api import configuration

# by using configuration you can add path value.
wkhtml_path = pdfkit.configuration(
    wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")


builds = Blueprint('builds', __name__)

@builds.route('/')
@login_required
def builds_home():
    blends = PowderBlends.query.all()
    return render_template("home.html", user=current_user, blends=blends)

from sqlalchemy import distinct

@builds.route('/builds', methods=['GET', 'POST'])
@login_required
def builds_page():
    if request.method == 'POST':
        if 'Facility' in request.form:
            selectedFacility = request.form.get("Facility")
            session['last_selected_facility'] = selectedFacility
        
        elif 'data_viewer' in request.form:
            flash("Load Data Viewer", category='success')
            return redirect(url_for('builds.data_viewer'))
        
        elif 'traveler' in request.form:
            flash("Make Traveler", category='success')
            return redirect(url_for('builds.generate_traveler_report'))
        
        
        
        
    selectedFacility = session.get('last_selected_facility')
    builds = []
    if selectedFacility is not None:
        builds = BuildsTable.query.filter_by(FacilityName=selectedFacility).order_by(desc(BuildsTable.BuildIt)).all()

    # Fetch all unique machine names and material names
    machines = [build.MachineID for build in builds]
    materials = [build.Material for build in builds]
    unique_machines = list(set(machines))
    unique_materials = list(set(materials))

    # You'll need to fetch the build information from the database
    # based on the selected build ID (use the selectedBuildID variable)
    selectedBuildID = request.form.get("solidJobsBuildIDInput")
    selectedBuild = BuildsTable.query.filter_by(BuildIt=selectedBuildID).first()

    return render_template('builds.html', user=current_user, current_build=selectedBuild, buildsInfo=builds,
                           machines=unique_machines, materials=unique_materials)





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
    


@builds.route('/data_viewer')
@login_required
def data_viewer():
    # Fetch all the data from the builds table
    all_builds = BuildsTable.query.all()

    # Pagination logic
    per_page = 150
    current_page = int(request.args.get('page', 1))
    total_builds = len(all_builds)
    num_pages = ceil(total_builds / per_page)
    start = (current_page - 1) * per_page
    end = start + per_page

    return render_template('data_viewer.html', user=current_user, builds=all_builds[start:end], current_page=current_page, num_pages=num_pages)





@builds.route('/export_csv', methods=['POST'])
@login_required
def export_csv():
    # Fetch all the data from the builds table
    all_builds = BuildsTable.query.all()

    # Get the column names from the BuildsTable
    column_names = [column.name for column in BuildsTable.__table__.columns]

    # Create a DataFrame from the data
    df = pd.DataFrame([[getattr(build, column) for column in column_names] for build in all_builds],
                      columns=column_names)

    # Export the DataFrame to a CSV file
    csv_data = df.to_csv(index=False)

    # Create a Flask Response object with the CSV data
    response = Response(csv_data, content_type='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=builds_data.csv"

    return response

@builds.route('/traveler_report', methods=['GET', 'POST'])
@login_required
def generate_traveler_report():
    # Get the data from the forms or database and populate the fields
    field1_value = "Value 1"  # Replace with your actual data
    field2_value = "Value 2"  # Replace with your actual data

    # Render the HTML template with the data
    rendered = render_template('traveler_report.html', field1_value=field1_value, field2_value=field2_value)

    # Generate the PDF
    pdf = pdfkit.from_string(rendered, False,configuration=wkhtml_path)

    # Create a Flask Response object with the PDF data
    response = make_response(pdf)
    response.headers['Content-type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=traveler_report.pdf'
    

    return response

@builds.route('/new_build', methods=['POST'])
@login_required
def new_build():
    # Get the highest BuildIt number from the database
    highest_buildit = db.session.query(func.max(BuildsTable.BuildIt)).scalar()

    # Increment the BuildIt number by 1 for the new build
    new_buildit = highest_buildit + 1

    # Retrieve the selected facility from the form or session
    selected_facility = request.form.get("Facility")  # Replace "Facility" with the correct field name from your form

    # Create a new record with the BuildIt number and FacilityName
    new_build = BuildsTable(BuildIt=new_buildit, FacilityName="Austin")

    db.session.add(new_build)
    db.session.commit()

    # Redirect to the builds page with the new build selected
    return redirect(url_for('builds.builds_page', selectedBuildID=new_buildit))



@builds.route('/copy_build', methods=['POST'])
@login_required
def copy_build():
    # Get the selected build ID from the form
    selected_buildid = int(request.form.get('solidJobsBuildIDInput'))

    # Get the highest BuildIt number from the database
    highest_buildit = db.session.query(func.max(BuildsTable.BuildIt)).scalar()

    # Increment the BuildIt number by 1 for the new build
    new_buildit = highest_buildit + 1

    # Get the existing build record
    existing_build = BuildsTable.query.filter_by(BuildIt=selected_buildid).first()

    if existing_build:
        # Create a new record with the same data as the existing build but with a new BuildIt number
        new_build = BuildsTable(BuildIt=new_buildit, MachineID=existing_build.MachineID,
                                Material=existing_build.Material, MinCharge=existing_build.MinCharge,
                                MaxCharge=existing_build.MaxCharge, XScale=existing_build.XScale,
                                YScale=existing_build.YScale, BeamOffset=existing_build.BeamOffset,
                                LayerThickness=existing_build.LayerThickness, PlatformTemp=existing_build.PlatformTemp,
                                # Include all other columns from the table that need to be copied
                                )

        db.session.add(new_build)
        db.session.commit()

    # Redirect to the builds page with the new build selected
    return redirect(url_for('builds.builds_page', selectedBuildID=new_buildit))
