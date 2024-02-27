from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, Response, make_response
from flask_login import login_required, current_user
import datetime as dt
from sqlalchemy import func, desc, or_
import pandas as pd
import math
from . import db
from .models import NcrsTable, Users, Location

ncrs = Blueprint('ncrs', __name__)


@ncrs.route('/home', methods=['GET', 'POST'])
@login_required
def ncrs_home():
    return redirect(url_for('ncrs.ncrs_page'))

@ncrs.route('/', methods=['GET', 'POST'])
@login_required
def ncrs_page():
    # Get the selected facility and search input from the form or query parameters
    selectedFacility = request.form.get('facilitySelectInput') or request.args.get('selectedFacility')
    searchInput = request.form.get('SearchInput')
    # Store the selected facility in the session for future use
    if selectedFacility:
        session['last_selected_facility'] = selectedFacility
    else: 
        selectedFacility = session.get('last_selected_facility')
    # Retrieve NCRs based on selected facility and search input
    ncrs = NcrsTable.query
    if selectedFacility:
        location = Location.query.filter_by(LocationID=selectedFacility).first()
        if location:
            ncrs = ncrs.filter_by(LocationID=selectedFacility)
    if searchInput:
        ncrs = ncrs.filter(or_(
            NcrsTable.NCRID.contains(searchInput),
            NcrsTable.WorkOrderNumber.contains(searchInput)
        ))
    ncrs = ncrs.order_by(desc(NcrsTable.NCRID)).all()
    selectedNCRID = request.form.get('NCRIDInput')
    selectedNCR = NcrsTable.query.filter_by(NCRID=selectedNCRID).first()
    selectedNCRCreatedOn = None
    
    if request.method == 'POST':
        if 'data_viewer' in request.form:
            flash('Load Data Viewer', category='success')
            return redirect(url_for('ncrs.data_viewer'))
        elif 'NCRForm' in request.form:
            session['NCRForm'] = request.form.to_dict()
            return redirect(url_for('ncrs.NCRForm'))

        
    return render_template(
        'NCRS/NCRS.html', 
        user=current_user, 
        current_ncr=selectedNCR, 
        ncrsInfo=ncrs,
        selectedFacility=selectedFacility,
        LocationTable=Location.query.all()
        )


@ncrs.route('get_NCR_info/<int:ncr_id>', methods=['GET'])
def get_ncr_info(ncr_id):
    # Assuming you have a database table named 'NcrsTable' with a column named 'NCRID'
    # ncr = NcrsTable.query.get(ncr_id)
    ncr, first_name, last_name, location_name = db.session.query(
        NcrsTable,
        Users.first_name,
        Users.last_name,
        Location.LocationName
    ).join(
        Users,
        NcrsTable.CreatedBy == Users.id
    ).join(
        Location,
        NcrsTable.LocationID == Location.LocationID
    ).filter(
        NcrsTable.NCRID == ncr_id
    ).first()
    if ncr:
        # Return the filtered NCR information as JSON
        ncr.CreatedBy = f'{first_name} {last_name}'
        ncr.LocationName = location_name
        ncr_data = ncr.to_dict()
        session['NCRIDInput'] = ncr_id
        return jsonify(ncr_data)
    else:
        # If NCR ID is not found, return an empty response with 404 status code
        return jsonify({'error': 'NCR not found'}), 404
    
@ncrs.route('/data_viewer', methods=['GET', 'POST'])
@login_required
def data_viewer():
    # Fetch all the data from the NCRs table
    all_ncrs = NcrsTable.query.all()
    # Pagination logic
    PER_PAGE = 150
    current_page = int(request.args.get('page', 1))
    total_ncrs = len(all_ncrs)
    num_pages = math.ceil(total_ncrs / PER_PAGE)
    start = (current_page - 1) * PER_PAGE
    end = start + PER_PAGE
    return render_template(
        'ncrs/data_viewer.html', 
        user=current_user, 
        ncrs=all_ncrs[start:end], 
        current_page=current_page, 
        num_pages=num_pages
        )

@ncrs.route('/export_csv', methods=['POST'])
@login_required
def export_csv():
    # Fetch all the data from the NCRs table
    all_ncrs = NcrsTable.query.all()
    # Get the column names from the NcrsTable
    column_names = [column.name for column in NcrsTable.__table__.columns]
    # Create a DataFrame from the data
    df = pd.DataFrame([[getattr(ncr, column) for column in column_names] for ncr in all_ncrs], columns=column_names)
    # Export the DataFrame to a CSV file
    csv_data = df.to_csv(index=False)
    # Create a Flask Response object with the CSV data
    response = Response(csv_data, content_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=ncrs_data.csv'
    return response


@ncrs.route('/new_ncr', methods=['POST'])
@login_required
def new_ncr():
    # Get the highest NCRID number from the database
    highest_ncr_id = db.session.query(func.max(NcrsTable.NCRID)).scalar()
    # Increment the NCRID number by 1 for the new NCR
    new_ncr_id = highest_ncr_id + 1
    # Retrieve the selected facility from the form or session
    selectedFacility = request.form.get('facilitySelectInput')
    if not selectedFacility:
        selectedFacility = session.get('last_selected_facility')
        print(selectedFacility)
    # Create a new record with the NCRID number and FacilityName
    location = Location.query.filter_by(LocationID=selectedFacility).first()
    if location:
        new_ncr = NcrsTable(
            NCRID=new_ncr_id, 
            LocationID=location.LocationID,
            CreatedBy=current_user.id, 
            CreatedOn=dt.datetime.now())
        db.session.add(new_ncr)
        db.session.commit()
        
        
        # Redirect to the NCRs page with the new NCR selected
        return redirect(url_for('ncrs.ncrs_page', selectedFacility=selectedFacility, selectedNCRID=new_ncr_id))
    else:
        flash(f'Location {selectedFacility} not found.', category='error')
        return redirect(url_for('ncrs.ncrs_page'))


def set_attributes(existing_ncr, attributes, dtype, ncrform_data):
    for attr in attributes:
        if (dtype == 'str') or (dtype == 'string'):
            try:
                value = str(ncrform_data.get(f'{attr}'))
            except (TypeError, ValueError) as e:
                value = ''  # Default value
        elif (dtype == 'float'):
            try:
                value = float(ncrform_data.get(f'{attr}'))
            except (TypeError, ValueError) as e:
                value = None  # Default value
        elif (dtype == 'int') or (dtype == 'integer'):
            try:
                value = int(ncrform_data.get(f'{attr}'))
            except (TypeError, ValueError) as e:
                value = 0  # Default value
        elif (dtype == 'bool'):
            try:
                value = bool(ncrform_data.get(f'{attr}'))
            except (TypeError, ValueError) as e:
                value = False  # Default value
        attr = attr.replace('Input', '')
        if not hasattr(existing_ncr, attr):
            print(f'Bad Attribute! "{attr}": {value}')
            flash(f'NcrsTable has no attribute "{attr}"!', category='error')
        else:
            setattr(existing_ncr, attr, value)
            # Save the changes to the database
            db.session.commit()

@ncrs.route('/NCRForm', methods=['GET', 'POST'])
@login_required
def NCRForm():
    # Get the NCR form data from the session
    ncrform_data = session.get('NCRForm')
    # Get the selected NCR id
    selected_ncr_id = session.get('NCRIDInput')
    # Retrieve the existing NCR record from the database
    existing_ncr = NcrsTable.query.filter_by(NCRID=selected_ncr_id).first()

    if existing_ncr and ncrform_data:
        # Define attribute mappings with their respective data types
        attribute_mappings = {
            'CategoryInput': 'str',
            'DescriptionInput': 'str',
            'QuantityInput': 'int',
            'WorkOrderInput': 'int'
        }
        for attr, dtype in attribute_mappings.items():
            value = ncrform_data.get(attr)
            # Check if the attribute exists in the NCR model
            if hasattr(existing_ncr, attr):
                try:
                    # Convert the value to the specified data type
                    if dtype == 'str':
                        setattr(existing_ncr, attr, str(value))
                    elif dtype == 'int':
                        setattr(existing_ncr, attr, int(value))
                    # Save the changes to the database
                    db.session.commit()
                except (ValueError, TypeError) as e:
                    flash(f'Error updating {attr}: {e}', category='error')
        flash(f'NCRForm information updated successfully for NCRID {selected_ncr_id}.', category='success')
        return redirect(url_for('ncrs.ncrs_page'))
    
    # Handle cases when the existing NCR or form data is not found
    flash(f'NCRID {selected_ncr_id} not found or form data missing.', category='error')
    return redirect(url_for('ncrs.ncrs_page', selectedNCRID=selected_ncr_id))
