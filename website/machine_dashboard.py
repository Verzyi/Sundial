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
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text
from flask import current_app





# from .models_status import StatusTable

# Create a Blueprint for your views
machine_dashboard = Blueprint('machine_dashboard', __name__)
bcrypt = Bcrypt()



# Define the dashboard function
def dashboard(app):
    with app.app_context():
        try:
            from .models_status import StatusTable
            from .models_status import db
            directory = os.path.dirname(os.path.realpath(__file__))

            sys.path.append("../")
            logging.debug('\n{0}; Importing local libraries'.format(datetime.now()))


            austin_rows = [
            ['Last Updated: {}'.format(datetime.now().strftime('%m/%d/%y %I:%M %p'))],
            ['Machine', 'Status', 'Material', 'End Date & Time', 'Time Remaining (hr)', 'Current Build',
            'Current Job(s)', 'Notes', 'Recoater Type', 'Job(s) in Queue', 'PM Due']]


            # Statuses by types
            running_statuses = ['Exposure', 'Recoating', 'Next layer', 'Job start', 'ProcessResume']
            stopped_statuses = ['Exposure/Interrupt', 'Job end', 'Recoating/Interrupt', '-1', None]

            # print(directory)
            
            # Calculate the path to the 'instance' folder which is up one level from the current file
            instance_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
            db_file_path = os.path.join(instance_folder, 'dmls_status.db')

            conn = EOS_DB2_Wrapper.MachineData()

            for machine in conn.machines:
                logging.info('\n{0}; Connecting to machine {1}'.format(datetime.now(), machine))
                machine_return = getattr(conn, 'si{0}'.format(machine))
                try:
                    from .models_status import StatusTable
                    from .models_status import db
                    machine_return.fetch_status()
                except EOS_DB2_Wrapper.DB2ConnectionError:
                    # Log connection error
                    logging.info('\n; Connection Error')
                    
                except Exception as e:
                    # Log connection error
                    # print(e)
                    logging.info('\n; Connection Error')
                    pass

                # Pull last database status entry to compare to current.
                last_status_sql = text('SELECT id, machine, status, material FROM status_table WHERE machine=:machine ORDER BY id DESC LIMIT 1')
                try:
                    # Get a database connection from the engine
                    with db.get_engine(bind='dmls_status').connect() as connection:
                        # Execute the SQL statement with parameters
                        result = connection.execute(last_status_sql, {'machine': machine})
                        # Fetch the result row
                        last_status = result.fetchone()[-2]
                        last_material = result.fetchone()[-1]
                        last_id = result.fetchone()[0]

                        
                except TypeError:
                    last_status = None
                    last_material= None
                    last_id = db.session.query(StatusTable).order_by(StatusTable.id.desc()).first().id

                # Insert data into database before updating dashboard
                db_finish_datetime = machine_return.finish_datetime
                db_finish_datetime = None if db_finish_datetime is None else int(db_finish_datetime.strftime('%y%m%d%H%M%S'))
                build_material = last_material if machine_return.material is None else machine_return.material.lower()
                status_table = StatusTable(id=int(last_id)+1,
                                        timestamp=int(datetime.now().strftime('%y%m%d%H%M%S')),
                                        machine=machine_return.serial_number,
                                        status=machine_return.current_status,
                                        material=build_material,
                                        end_datetime=db_finish_datetime,
                                        time_remaining=machine_return.remaining_build_time,
                                        build_id=machine_return.build_id,
                                        current_height=machine_return.current_height)
                
                
                #get workorder number
                build_id = machine_return.build_id
                



                # Update Sheets dashboard
                status = machine_return.current_status
                # print(machine, last_status, status)
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
                machine_data = [[machine, status, material, finish_datetime, remaining_time, build_id]]
                if machine_return.site == 'Belton':
                    austin_rows += machine_data
                else:
                    austin_rows += machine_data

                    
                db.session.add(status_table)
                db.session.commit()    

            # Return the data
            # print(austin_rows)
            return austin_rows
        except Exception as e:
            logging.error(f"Error in dashboard function: {str(e)}")        

        
        
        
        
# Define the route for the dashboard
@machine_dashboard.route('/machine')
@login_required
def builds_home():
    data = dashboard()
    return render_template('dashboards/printers.html', user=current_user, machine_return=data[2:])



