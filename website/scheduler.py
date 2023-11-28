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
from .models import BuildsTable, Users, Tasks, TaskTypes, Machines, Location



scheduler = Blueprint('scheduler', __name__)


@scheduler.route('/scheduler', methods=['GET', 'POST'])
@login_required
def index():
    
    
    
    machines_in_austin = db.session.query(Machines.MachineAlias, Machines.MachineSerial)\
        .join(Location, Machines.LocationID == Location.LocationID)\
        .filter(Location.LocationName == 'Austin')\
        .all()
        
        
        
    
    


    return render_template('scheduler/scheduler.html',user=current_user, machine_return =machines_in_austin)



@scheduler.route('/unscheduled', methods=['GET', 'POST'])
@login_required
def unscheduled():
    
    builds = BuildsTable.query
    AllBuilds = builds.filter(BuildsTable.MachineID.isnot(None))
    builds = builds.filter(or_(BuildsTable.MachineID==None, BuildsTable.MachineID=="None" , BuildsTable.MachineID=="" ))
    builds = builds.order_by(desc(BuildsTable.BuildID)).all()
    # Fetch all unique machine names and material names
    machines = [build.MachineID for build in AllBuilds]
    materials = [build.AlloyName for build in AllBuilds]
    machines = list(set(machines))
    materials = list(set(materials))

    return render_template('scheduler/unscheduled-builds.html',user=current_user,builds= builds, machines = sorted(machines), materials= sorted(materials) )


@scheduler.route('/build-que', methods=['GET', 'POST'])
@login_required
def que():
    
    builds = BuildsTable.query
    AllBuilds = builds.filter(BuildsTable.MachineID.isnot(None))
    builds = builds.filter(or_(BuildsTable.BuildStartTime==None, BuildsTable.BuildStartTime=="None" , BuildsTable.BuildStartTime=="" ))
    builds = builds.order_by(desc(BuildsTable.BuildID)).all()
    # Fetch all unique machine names and material names
    machines = [build.MachineID for build in AllBuilds]
    materials = [build.AlloyName for build in AllBuilds]
    machines = list(set(machines))
    materials = list(set(materials))

    return render_template('scheduler/que-builds.html',user=current_user,builds= builds, machines = sorted(machines), materials= sorted(materials) )

@scheduler.route('/build-running', methods=['GET', 'POST'])
@login_required
def running():
    builds = BuildsTable.query
    AllBuilds = builds.filter(BuildsTable.MachineID.isnot(None))
    builds = builds.filter(BuildsTable.BuildFinishTime == None, BuildsTable.BuildStartTime != None)
    builds = builds.order_by(desc(BuildsTable.BuildID)).all()
    # Fetch all unique machine names and material names
    machines = [build.MachineID for build in AllBuilds]
    materials = [build.AlloyName for build in AllBuilds]
    machines = list(set(machines))
    materials = list(set(materials))

    return render_template('scheduler/running-builds.html', user=current_user, builds=builds, machines=sorted(machines), materials=sorted(materials))



@scheduler.route('/update_database', methods=['POST'])
def update_database():
    
    data = request.json  # Access JSON data using request.json
    print(data)


    builds = BuildsTable.query
    builds = builds.filter_by(BuildID=data["build_id"]).first()
    builds.MachineID = data["machine_id"]
    builds.AlloyName = data["material_name"]
    builds.BuildTime = data['build_time']
    builds.BuildStartTime = data['build_start_time']
    
    # Commit changes to the database
    db.session.commit()

    # Return a response indicating success or failure
    response_data = {'status': 'success', 'message': 'Database updated successfully'}
    return jsonify(response_data)






@scheduler.route('/tasks', methods=['GET'])
def get_tasks():
    builds = BuildsTable.query.filter_by(BuildFinishTime=None).all()  # Fetch tasks where BuildFinishTime is NULL
    # print(builds)
    
    # Convert the list of builds to a list of dictionaries
    tasks = []
    for build in builds:
        tasks.append({
            'BuildID': build.BuildID,
            'AlloyName': build.AlloyName,
            'MachineID': build.MachineID,
            'BuildStart': build.BuildStartTime,
            'BuildTime': build.BuildTime
        })

    
    
    
    # Return the tasks as JSON
    return jsonify(tasks)


