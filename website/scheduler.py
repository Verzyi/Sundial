from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, Response, make_response
from flask_login import login_required, current_user
import datetime as dt
from sqlalchemy import func, desc, or_, not_
import pandas as pd
from werkzeug.utils import secure_filename
import numpy as np
import os
import math
from . import db
from .models import BuildsTable, Users



scheduler = Blueprint('scheduler', __name__)


@scheduler.route('/scheduler', methods=['GET', 'POST'])
@login_required
def index():
    

    return render_template('scheduler/scheduler.html',user=current_user)



@scheduler.route('/unscheduled', methods=['GET', 'POST'])
@login_required
def unscheduled():
    
    builds = BuildsTable.query
    AllBuilds = builds.filter(BuildsTable.MachineID.isnot(None))
    builds = builds.filter(or_(BuildsTable.MachineID==None, BuildsTable.MachineID=="None" ))
    builds = builds.order_by(desc(BuildsTable.BuildID)).all()
    # Fetch all unique machine names and material names
    machines = [build.MachineID for build in AllBuilds]
    materials = [build.AlloyName for build in AllBuilds]
    machines = list(set(machines))
    materials = list(set(materials))
    # Fetch the build information from the database based on the selected build ID (use the selectedBuildID variable)
    selectedBuildID = request.form.get('BuildIDInput')
    selectedBuild = BuildsTable.query.filter_by(BuildID=selectedBuildID).first()
    selectedBuildCreatedOn = None
    

    return render_template('scheduler/unscheduled-builds.html',user=current_user,builds= builds, machines = sorted(machines), materials= sorted(materials) )


@scheduler.route('/update_database', methods=['POST'])
def update_database():
    
    data = request.json  # Access JSON data using request.json
    print(data)


    builds = BuildsTable.query
    builds = builds.filter_by(BuildID=data["build_id"]).first()
    builds.MachineID = data["machine_id"]
    builds.AlloyName = data["material_name"]
    
    # Commit changes to the database
    db.session.commit()

    # Return a response indicating success or failure
    response_data = {'status': 'success', 'message': 'Database updated successfully'}
    return jsonify(response_data)