from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, Response, make_response
from .models import PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func, join, desc
import socket
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
    # Get the selected facility and search input from the form or query parameters
    selectedFacility = request.form.get("facilitySelect") or request.args.get("selectedFacility")
    searchInput = request.form.get("SearchInput")

    # Store the selected facility in the session for future use
    if selectedFacility:
        session['last_selected_facility'] = selectedFacility
        
    else: 
        selectedFacility=session.get('last_selected_facility')
    
        

    # Retrieve builds based on selected facility and search input
    builds = BuildsTable.query
    if selectedFacility:
        builds = builds.filter_by(FacilityName=selectedFacility)
    if searchInput:
        builds = builds.filter(or_(
            BuildsTable.BuildIt.contains(searchInput),
            BuildsTable.BuildName.contains(searchInput)
        ))
    builds = builds.order_by(desc(BuildsTable.BuildIt)).all()

    # Fetch all unique machine names and material names
    machines = [build.MachineID for build in builds]
    materials = [build.Material for build in builds]
    unique_machines = list(set(machines))
    unique_materials = list(set(materials))

    # You'll need to fetch the build information from the database
    # based on the selected build ID (use the selectedBuildID variable)
    selectedBuildID = request.form.get("solidJobsBuildIDInput")
    selectedBuild = BuildsTable.query.filter_by(BuildIt=selectedBuildID).first()

    if request.method == 'POST':
        if 'data_viewer' in request.form:
            flash("Load Data Viewer", category='success')
            return redirect(url_for('builds.data_viewer'))
        elif 'traveler' in request.form:
            flash("Make Traveler", category='success')
            return redirect(url_for('builds.generate_traveler_report'))
        elif 'buildformSetup' in request.form:
            session['buildformSetup'] = request.form.to_dict()
            return redirect(url_for('builds.setup_form'))
        elif 'buildformStart' in request.form:
            session['buildformStart'] = request.form.to_dict()
            return redirect(url_for('builds.start_form'))
        elif 'buildformFinish' in request.form:
            session['buildformFinish'] = request.form.to_dict()
            return redirect(url_for('builds.finish_form'))
            
             

    return render_template('builds.html', user=current_user, current_build=selectedBuild, buildsInfo=builds,
                           machines=unique_machines, materials=unique_materials)
        
        

    return render_template('builds.html', user=current_user, current_build=selectedBuild, buildsInfo=builds,
                           machines=unique_machines, materials=unique_materials)




@builds.route('/get_build_info/<int:buildid>', methods=['GET'])
def get_build_info(buildid):
    # Assuming you have a database table named 'BuildsTable' with a column named 'BuildId'
    build = BuildsTable.query.get(buildid)
    if build:
        # Return the filtered build information as JSON
        build_data = build.to_dict()
        session['buildid'] = buildid
        return jsonify(build_data)
    else:
        # If build ID is not found, return an empty response with 404 status code
        return jsonify({"error": "Build not found"}), 404
    


@builds.route('/data_viewer', methods=['GET', 'POST'])
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
    selectedFacility = request.form.get("facilitySelect")
    if not selectedFacility:
        selectedFacility = session.get('last_selected_facility')

    # Create a new record with the BuildIt number and FacilityName
    new_build = BuildsTable(BuildIt=new_buildit, FacilityName=selectedFacility, CreatedBy=current_user.id, CreatedOn=datetime.now())

    db.session.add(new_build)
    db.session.commit()

    # Redirect to the builds page with the new build selected
    return redirect(url_for('builds.builds_page', selectedFacility=selectedFacility, selectedBuildID=new_buildit))




@builds.route('/copy_build', methods=['POST'])
@login_required
def copy_build():
    # Get the selected build ID from the form
    selected_buildid = session.get('buildid')
    print(selected_buildid)


    if selected_buildid:
        try:
            selected_buildid = int(selected_buildid)
        except ValueError:
            # Handle the case when the 'BuildsID' cannot be converted to an integer
            flash("Invalid Build ID format.", category='error')
            return redirect(url_for('builds.builds_page'))

        # Get the highest BuildIt number from the database
        highest_buildit = db.session.query(func.max(BuildsTable.BuildIt)).scalar()

        # Increment the BuildIt number by 1 for the new build
        new_buildit = highest_buildit + 1

        # Get the existing build record
        existing_build = BuildsTable.query.filter_by(BuildIt=selected_buildid).first()

        if existing_build:
            # Create a new record with the same data as the existing build but with a new BuildIt number
            new_build = BuildsTable(
                BuildIt=new_buildit,
                MachineID=MachineID,
                Material=Material,
                MinChargeAmount=MinChargeAmount,
                MaxChargeAmount=MaxChargeAmount,
                ScaleX=ScaleX,
                ScaleY=ScaleY,
                Offset=Offset,
                Layer=Layer,
                PlatformTemperature=PlatformTemperature,
                RecoaterSpeed=RecoaterSpeed,
                ParameterRev=ParameterRev,
                DosingBoostAmount=DosingBoostAmount,
                RecoaterType=RecoaterType,
                PotentialBuildHeight=PotentialBuildHeight,
                FacilityName=FacilityName,
                CreatedBy=current_user.id,
                CreatedOn=datetime.now()
                # Include all other columns from the table that need to be copied
            )

            db.session.add(new_build)
            db.session.commit()

            # Redirect to the builds page with the new build selected
            return redirect(url_for('builds.builds_page', selectedBuildID=new_buildit))

    # Handle the case when 'BuildsID' is not present in the form
    flash("No Build ID found in the form.", category='error')
    return redirect(url_for('builds.builds_page'))


from flask import request

@builds.route('/setup-form', methods=['GET', 'POST'])
@login_required
def setup_form():
    # Get the build form data from the session
    buildform_data = session.get('buildformSetup')
    
    # Get the selected build id
    selected_buildid = session.get('buildid')
    
    # Retrieve the existing build record from the database
    existing_build = BuildsTable.query.filter_by(BuildIt=selected_buildid).first()

    # Update the attributes of the existing build with the new values
    if existing_build:
        # Populate data from buildSetup
        existing_build.BuildName = buildform_data.get('buildNameInput')
        existing_build.MachineID = buildform_data.get('machineInput')
        existing_build.Material = buildform_data.get('materialInput')
        existing_build.ParameterRev = buildform_data.get('parameterRevInput')
        existing_build.RecoaterType = buildform_data.get('recoaterTypeInput')
        
        # Iterate through the attributes that might have float values
        float_attributes = ['ScaleX', 'ScaleY', 'Offset', 'Layer' , 'PlatformTemperature', 'PotentialBuildHeight',
                            'MinChargeAmount', 'MaxChargeAmount', 'DosingBoostAmount', 'RecoaterSpeed']
        for attr in float_attributes:
            try:
                value = float(buildform_data.get(f'{attr}Input', 0))  # Use 0 as default if conversion fails
            except ValueError:
                value = 0  # Default value in case of ValueError
            setattr(existing_build, attr, value)
        
        # db.session.add(existing_build)
        # Save the changes to the database
        db.session.commit()

        # Redirect to the builds page or any other page as needed
        flash("Build Setup information updated successfully.", category='success')
        return redirect(url_for('builds.builds_page'))

    # Handle the case when the existing build is not found
    flash("Build not found.", category='error')
    return redirect(url_for('builds.builds_page'))


@builds.route('/start-form', methods=['GET', 'POST'])
@login_required
def start_form():
    # Get the build form data from the session
    buildform_data = session.get('buildformStart')
    
    # Get the selected build id
    selected_buildid = session.get('buildid')
    
    # Retrieve the existing build record from the database
    existing_build = BuildsTable.query.filter_by(BuildIt=selected_buildid).first()

    # Update the attributes of the existing build with the new values
    if existing_build:
        #Populate data from buildStart
        existing_build.InertTime = buildform_data.get('InertTimeInput')
        existing_build.F9FilterSerial = buildform_data.get('F9FilterSerialInput')
        existing_build.H13FilterSerial = buildform_data.get('H13FilterSerialInput')    
        existing_build.BuildStart = buildform_data.get('BuildStartInput')
        
        # Populate data from buildStartForm (float attributes)
        start_form_float_attributes = ['PlateThickness', 'PlatformWeight', 'FeedPowderHeight', 'StartLaserHours']
        for attr in start_form_float_attributes:
            try:
                value = float(buildform_data.get(f'{attr}Input', 55))  # Use 0 as default if conversion fails
            except ValueError:
                print("error")
                value = 0  # Default value in case of ValueError
            setattr(existing_build, attr, value)
        
        # Populate data from buildStartForm (integer attributes)
        integer_attributes = ['BlendID', 'PlateSerial']
        for attr in integer_attributes:
            try:
                value = int(buildform_data.get(f'{attr}Input', 0))  # Use 0 as default if conversion fails
            except ValueError:
                value = 0  # Default value in case of ValueError
            setattr(existing_build, attr, value)
            
        
        db.session.commit()

        # Redirect to the builds page or any other page as needed
        flash("Build Start information updated successfully.", category='success')
        return redirect(url_for('builds.builds_page'))

    # Handle the case when the existing build is not found
    flash("Build not found.", category='error')
    return redirect(url_for('builds.builds_page'))

            
            
            
@builds.route('/finish-form', methods=['GET', 'POST'])
@login_required
def finish_form():
    # Get the build form data from the session
    buildform_data = session.get('buildformFinish')
    
    # Get the selected build id
    selected_buildid = session.get('buildid')
    
    # Retrieve the existing build record from the database
    existing_build = BuildsTable.query.filter_by(BuildIt=selected_buildid).first()

    # Update the attributes of the existing build with the new values
    if existing_build:
        
        existing_build.Breakout = buildform_data.get('BreakoutInput') 
        
        existing_build.MaterialAdded = buildform_data.get('MaterialAddedInput') == 'True'
        print("Material Added Input:", existing_build.MaterialAdded)

        # existing_build.MaterialAdded = material_added_input == True
        
        existing_build.BuildInterrupts = buildform_data.get('BuildInterruptsInput') == 'True'
        print("Build Interrupts Input:", existing_build.BuildInterrupts)
        

        # existing_build.BuildInterrupts = build_interrupts_input == True
        
        
        
        


        
        # Populate data from buildFinishForm
        finish_form_float_attributes = ['FinishHeight', 'EndPartPistonHeight', 'EndFeedPowderHeight', 'BuildTime', 'FinalLaserHours','FinishPlatformWeight']
        for attr in finish_form_float_attributes:
            try:
                value = float(buildform_data.get(f'{attr}Input', 0))  # Use 0 as default if conversion fails
            except ValueError:
                value = 0  # Default value in case of ValueError
            setattr(existing_build, attr, value)
        
        
        db.session.commit()

        # Redirect to the builds page or any other page as needed
        flash("Build Finished information updated successfully.", category='success')
        return redirect(url_for('builds.builds_page'))

    # Handle the case when the existing build is not found
    flash("Build not found.", category='error')
    return redirect(url_for('builds.builds_page'))

