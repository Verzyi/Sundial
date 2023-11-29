from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, Response, make_response
from flask_login import login_required, current_user
import datetime as dt
from sqlalchemy import func, desc, or_
import pandas as pd
import math
import pdfkit

from . import db
from .models import NcrsTable, Users

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
        selectedFacility=session.get('last_selected_facility')
    # Retrieve NCRs based on selected facility and search input
    ncrs = NcrsTable.query
    if selectedFacility:
        ncrs = ncrs.filter_by(LocationID=selectedFacility)
    if searchInput:
        ncrs = ncrs.filter(or_(
            NcrsTable.NCRID.contains(searchInput),
            NcrsTable.NCRName.contains(searchInput)
        ))
    ncrs = ncrs.order_by(desc(NcrsTable.NCRID)).all()
    selectedNCRID = request.form.get('NCRIDInput')
    selectedNCR = NcrsTable.query.filter_by(NCRID=selectedNCRID).first()
    selectedNCRCreatedOn = None
    
    if request.method == 'POST':
        if 'data_viewer' in request.form:
            flash('Load Data Viewer', category='success')
            return redirect(url_for('ncrs.data_viewer'))
        elif 'traveler' in request.form:
            flash('Make Traveler', category='success')
            return redirect(url_for('ncrs.generate_traveler_report'))
        elif 'ncrformSetup' in request.form:
            session['ncrformSetup'] = request.form.to_dict()
            return redirect(url_for('ncrs.setup_form'))
        elif 'ncrformStart' in request.form:
            session['ncrformStart'] = request.form.to_dict()
            return redirect(url_for('ncrs.start_form'))
        elif 'ncrformFinish' in request.form:
            session['ncrformFinish'] = request.form.to_dict()
            return redirect(url_for('ncrs.finish_form'))
        
    return render_template(
        'NCRS/NCRS.html', 
        user=current_user, 
        current_ncr=selectedNCR, 
        ncrsInfo=ncrs,
        selectedFacility=selectedFacility
        )


@ncrs.route('get_NCR_info/<int:ncr_id>', methods=['GET'])
def get_ncr_info(ncr_id):
    # Assuming you have a database table named 'NcrsTable' with a column named 'NCRID'
    # ncr = NcrsTable.query.get(ncr_id)
    ncr, first_name, last_name = db.session.query(
                NcrsTable,
                Users.first_name,
                Users.last_name
                ).join(
                    Users,
                    NcrsTable.CreatedBy == Users.id
                    ).filter(
                        NcrsTable.NCRID == ncr_id
                        ).first()
    if ncr:
        # Return the filtered NCR information as JSON
        ncr.CreatedBy = f'{first_name} {last_name}'
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
    # Create a new record with the NCRID number and FacilityName
    new_ncr = NcrsTable(
        NCRID=new_ncr_id, 
        FacilityName=selectedFacility, 
        CreatedBy=current_user.id, 
        CreatedOn=dt.datetime.now())
    db.session.add(new_ncr)
    db.session.commit()
    
    #adding task for task Schedule
    # Get the highest taskID number from the database
    highest_task_id = db.session.query(func.max(Tasks.TaskID)).scalar()
    # Increment the NCRID number by 1 for the new NCR
    new_task_id = highest_task_id + 1
            
    new_task = Tasks(
        TaskID = new_task_id,
        TaskName=new_ncr_id,
        TaskTypeID=1,
        TaskEstimateLength=1
        )
    
    # Redirect to the NCRs page with the new NCR selected
    return redirect(url_for('ncrs.ncrs_page', selectedFacility=selectedFacility, selectedNCRID=new_ncr_id))



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

@ncrs.route('/setup_form', methods=['GET', 'POST'])
@login_required
def setup_form():
    # Get the NCR form data from the session
    ncrform_data = session.get('ncrformSetup')
    # Get the selected NCR id
    selected_ncr_id = session.get('NCRIDInput')
    # Retrieve the existing NCR record from the database
    existing_ncr = NcrsTable.query.filter_by(NCRID=selected_ncr_id).first()
    # Update the attributes of the existing NCR with the new values
    if existing_ncr:
        # Iterate through the attributes that have string values
        str_attributes = ['CategoryInput', 'DescriptionInput']
        set_attributes(existing_ncr, str_attributes, 'str', ncrform_data)
        # Iterate through the attributes that have integer values
        int_attributes = ['QuantityInput', 'WorkOrderNumberInput']
        set_attributes(existing_ncr, int_attributes, 'int', ncrform_data)
        flash(f'NCR Setup information updated successfully for NCRID {selected_ncr_id}.', category='success')
        # Redirect to the NCRs page or any other page as needed
        return redirect(url_for('ncrs.ncrs_page'))
    # Handle the case when the existing NCR is not found
    flash(f'NCRID {selected_ncr_id} not found.', category='error')
    return redirect(url_for('ncrs.ncrs_page', selectedNCRID=selected_ncr_id))
