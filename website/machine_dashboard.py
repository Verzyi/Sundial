import EOS_DB2_Wrapper
import logging
import os
from datetime import datetime
import time
import sys
import sqlite3
from flask import Blueprint, redirect, url_for, flash,render_template,request
from flask_login import current_user, login_required
from flask_admin import Admin
from flask_admin.menu import MenuCategory
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt, check_password_hash 
import ibm_db


# Create a Blueprint for your views
machine_dashboard = Blueprint('machine_dashboard', __name__)
bcrypt = Bcrypt()
@machine_dashboard.route('/machine')
@login_required
def builds_home():
    data = dashboard()
    return render_template('dashboards/printers.html', user=current_user, machine_return=data)


def dashboard():
    directory = os.path.dirname(os.path.realpath(__file__))

    sys.path.append("../")
    logging.debug('\n{0}; Importing local libraries'.format(datetime.now()))


    austin_rows = [['Last Updated: {}'.format(datetime.now().strftime('%m/%d/%y %I:%M %p'))],
                ['Machine', 'Status', 'Material', 'End Date & Time', 'Time Remaining (hr)', 'Current Build',
                    'Current Job(s)', 'Notes', 'Recoater Type', 'Quals', 'Job(s) in Queue', 'PM Due']]


    # Statuses by types
    running_statuses = ['Exposure', 'Recoating', 'Next layer', 'Job start', 'ProcessResume']
    stopped_statuses = ['Exposure/Interrupt', 'Job end', 'Recoating/Interrupt', '-1', None]
    # stopped_statuses = ['Connection Error', 'Exposure/Interrupt', 'Job end', 'Recoating/Interrupt', '-1', None]

    print(directory)
    
    # Calculate the path to the 'instance' folder which is up one level from the current file
    instance_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    db_file_path = os.path.join(instance_folder, 'dmls_status.db')

    sqlite_conn = sqlite3.connect(db_file_path)
    cur = sqlite_conn.cursor()
    conn = EOS_DB2_Wrapper.MachineData()

    for machine in conn.machines:
        logging.info('\n{0}; Connecting to machine {1}'.format(datetime.now(), machine))
        machine_return = getattr(conn, 'si{0}'.format(machine))
        try:
            machine_return.fetch_status()
        except EOS_DB2_Wrapper.DB2ConnectionError:
            # Log connection error
            logging.info('\n; Connection Error')
            
        except Exception as e:
            # Log connection error
            print(e)
            logging.info('\n; Connection Error')
            pass

        # Pull last database status entry to compare to current.
        last_status_sql = 'SELECT id, machine, status FROM status_table WHERE machine="{0}" ORDER BY id DESC LIMIT 1'
        try:
            last_status = cur.execute(last_status_sql.format(machine)).fetchone()[-1]
        except TypeError:
            last_status = None

        # Insert data into database before updating dashboard
        db_finish_datetime = machine_return.finish_datetime
        db_finish_datetime = None if db_finish_datetime is None else int(db_finish_datetime.strftime('%y%m%d%H%M%S'))
        build_material = None if machine_return.material is None else machine_return.material.lower()
        cur.execute('INSERT INTO status_table ("timestamp", "machine", "status", "material", "end_datetime", '
            '"time_remaining", "build_id", "current_height") VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (int(datetime.now().strftime('%y%m%d%H%M%S')), machine_return.serial_number,
            machine_return.current_status, build_material, db_finish_datetime,
            machine_return.remaining_build_time, machine_return.build_id, machine_return.current_height))
        
        #get workorder number
        build_id = machine_return.build_id
        



        # Update Sheets dashboard
        status = machine_return.current_status
        print(machine, last_status, status)
        logging.info('\n{0}; Last Status: {1}, Current Status: {2}'.format(datetime.now(), last_status, status))
        status = 'Running' if status in running_statuses else status

        material = machine_return.material
        finish_datetime = machine_return.finish_datetime
        finish_datetime = '' if finish_datetime is None else finish_datetime.strftime('%m/%d/%y %I:%M %p')
        if machine_return.remaining_build_time not in [None, '0.00', 0.0]:
            remaining_time = '%.2f' % machine_return.remaining_build_time
        else:
            remaining_time = ''
        build_id = machine_return.build_id
        machine_data = [[None, status, material, finish_datetime, remaining_time, build_id]]
        if machine_return.site == 'Austin':
            austin_rows += machine_data
        else:
            austin_rows += machine_data
        sqlite_conn.commit()

        # Send updates for a status change
        if last_status == machine_return.current_status:
            # This continues if there is no change from the last status to the current. This prevents sending out messages
            # if users have already been notified.
            continue

        if last_status in running_statuses and machine_return.current_status in running_statuses:
            # This continues if the machine continues to run whether scanning, recoating, etc.
            continue

        if last_status in running_statuses and machine_return.current_status in stopped_statuses:
            # This identifies if the machine goes from a "good" state to a "bad" state

            title = 'SI{0}'.format(machine)
            body = 'Status change: {0} to {1}'.format(last_status, machine_return.current_status)

            if machine_return.site == 'Belton':
                # update for Belton channel
                logging.info('\n{0}; Sending Belton Notification'.format(datetime.now()))
                try:
                    # Put an action in here if notifications are to be added
                    pass
                except requests.exceptions.ConnectionError:
                    logging.warning('\n{0}; Belton Notification Failed to send'.format(datetime.now()))
                    pass
            if machine_return.site == 'Austin':
                # Update for Austin channel
                logging.warning('\n{0}; Sending Austin Notification'.format(datetime.now()))
                try:
                    # Put an action in here if notifications are to be added
                    pass
                except requests.exceptions.ConnectionError:
                    logging.info('\n{0}; Austin Notification Failed to send'.format(datetime.now()))
                    pass

    sqlite_conn.close()
