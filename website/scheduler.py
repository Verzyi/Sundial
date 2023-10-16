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
    # Define your machines mapping
    machines_mapping = {
            "M1": "1849",
            "M2": "1848",
            "M3": "1476",
            "M4": "1991",
            "M5": "2001",
            "M6": "2006",
            "M7": "1989",
            "M8": "1160",
            "M9": "1852",
            "M10": "1810",
            "M11": "1853",
            "M12": "1351",
            "M13": "2643",
            "M14": "2642",
            "M15": "1882",
            "M16": "3607",
            "M17": "2813"
        }
    
    
    builds = BuildsTable.query
    AllBuilds = builds.filter(BuildsTable.MachineID.isnot(None))
    builds = builds.filter(BuildsTable.MachineID.isnot(None))
    builds = builds.filter(BuildsTable.BuildFinishTime==None)
    builds = builds.order_by(desc(BuildsTable.BuildID)).all()
    # Fetch all unique machine names and material names
    machines = [build.MachineID for build in AllBuilds]
    materials = [build.AlloyName for build in AllBuilds]
    machines = list(set(machines))
    materials = list(set(materials))


    return render_template('scheduler/scheduler.html',user=current_user, machine_return =machines_mapping, builds= builds, machines = sorted(machines), materials= sorted(materials))



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


@scheduler.route('/update_database', methods=['POST'])
def update_database():
    
    data = request.json  # Access JSON data using request.json
    print(data)


    builds = BuildsTable.query
    builds = builds.filter_by(BuildID=data["build_id"]).first()
    builds.MachineID = data["machine_id"]
    builds.AlloyName = data["material_name"]
    builds.BuildTime = data['build_time']
    
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