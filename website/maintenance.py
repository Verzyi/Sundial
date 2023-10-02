from flask import Blueprint
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, render_template
from .models import Maintenance, db
from flask import request, render_template
from .models import Maintenance, db
from flask import Blueprint, render_template, request
from .models import Maintenance, db

maintenance_bp = Blueprint('maintenance', __name__)



db = SQLAlchemy()





    # Define the route for the form submission
@maintenance_bp.route('/request_work_order', methods=['GET', 'POST'])
def request_work_order():
    if request.method == 'POST':
        # Get the form data
        work_order = Maintenance(
                Work_Order=request.form['work_order'],
                Created_On=request.form['created_on'],
                Due_Date=request.form['due_date'],
                Next_Due_Date=request.form['next_due_date'],
                End_Due_Date=request.form['end_due_date'],
                Updated_On=request.form['updated_on'],
                Completed_On=request.form['completed_on'],
                Work_Order_Title=request.form['work_order_title'],
                Work_Order_Description=request.form['work_order_description'],
                Additional_Cost=request.form['additional_cost'],
                Labor_Cost=request.form['labor_cost'],
                Parts_Cost=request.form['parts_cost'],
                Total_Cost=request.form['total_cost'],
                Time=request.form['time'],
                Status=request.form['status'],
                Category=request.form['category'],
                Reschedule_Based_On_Completion=request.form['reschedule_based_on_completion'],
                Repeating_Schedule=request.form['repeating_schedule'],
                Root_Work_Order_Exists=request.form['root_work_order_exists'],
                Asset_ID=request.form['asset_id'],
                Asset_Name=request.form['asset_name'],
                Asset_Category=request.form['asset_category'],
                Asset_Area=request.form['asset_area'],
                Asset_Barcode=request.form['asset_barcode'],
                Location_Name=request.form['location_name'],
                Location_Address=request.form['location_address'],
                Location_ID=request.form['location_id'],
                Completed_By=request.form['completed_by'],
                Completed_By_ID=request.form['completed_by_id'],
                Requires_Signature=request.form['requires_signature'],
                Signature_Image=request.form['signature_image'],
                Assigned_By=request.form['assigned_by'],
                Assigned_By_ID=request.form['assigned_by_id'],
                Assigned_To=request.form['assigned_to'],
                Assigned_To_ID=request.form['assigned_to_id'],
                Team_Assigned=request.form['team_assigned'],
                Team_Assigned_ID=request.form['team_assigned_id'],
                Parts=request.form['parts'],
                Purchase_Orders=request.form['purchase_orders'],
                Estimated_Duration=request.form['estimated_duration'],
                Updates=request.form['updates'],
                Priority=request.form['priority'],
                Archived_Status=request.form['archived_status'],
                Images=request.form['images'],
                Checklist_ID=request.form['checklist_id'],
                Task_Data=request.form['task_data'],
                Task_Images=request.form['task_images'],
                Additional_Workers=request.form['additional_workers'],
                Additional_Worker_IDs=request.form['additional_worker_ids'],
                Requested_By=request.form['requested_by'],
                Requested_By_ID=request.form['requested_by_id'],
                Requested_By_Email_Address=request.form['requested_by_email_address'],
                Part_IDs=request.form['part_ids'],
                Part_Quantities=request.form['part_quantities'],
                File_IDs=request.form['file_ids']
            )
            # Add the new work order to the database
        db.session.add(work_order)
        db.session.commit()
        return 'Work order submitted successfully'
    else:
        # Render the form template
        return render_template('request_work_order.html')


# Define the route for the form submission
@maintenance_bp.route('/request_work_order', methods=['GET', 'POST'])
def request_work_order():
    # Your code for handling form submission goes here
    pass

# Define the route for viewing all requests
@maintenance_bp.route('/view_requests', methods=['GET'])
def view_requests():
    # Retrieve all requests from the database
    requests = Maintenance.query.all()
    # Render the template with the requests data
    return render_template('requests.html', requests=requests)



# Define the route for the form submission
@maintenance_bp.route('/request_work_order', methods=['GET', 'POST'])
def request_work_order():
    # Your code for handling form submission goes here
    pass

# Define the route for viewing all requests
@maintenance_bp.route('/view_requests', methods=['GET'])
def view_requests():
    # Retrieve all requests from the database
    requests = Maintenance.query.all()

    # Filter by Reactive or Repeating
    filter_type = request.args.get('filter_type')
    if filter_type == 'Reactive Only':
        requests = [r for r in requests if not r.Repeating_Schedule]
    elif filter_type == 'Repeating Only':
        requests = [r for r in requests if r.Repeating_Schedule]

    # Filter by Asset
    asset = request.args.get('asset')
    if asset:
        requests = [r for r in requests if r.Asset_Name == asset]




    # Define the route for the form submission
    @maintenance_bp.route('/request_work_order', methods=['GET', 'POST'])
    def request_work_order():
        # Your code for handling form submission goes here
        pass

    # Define the route for viewing all requests
    @maintenance_bp.route('/view_requests', methods=['GET'])
    def view_requests():
        # Retrieve all requests from the database
        search_query = request.args.get('search_query', '')
        if search_query:
            requests = Maintenance.query.filter(Maintenance.Work_Order_Title.ilike(f'%{search_query}%')).all()
        else:
            requests = Maintenance.query.all()

        # Filter by Team
        team = request.args.get('team')
        if team:
            requests = [r for r in requests if r.Team_Assigned == team]

        # Filter by Category
        category = request.args.get('category')
        if category:
            requests = [r for r in requests if r.Category == category]

        # Filter by Part
        part = request.args.get('part')
        if part:
            requests = [r for r in requests if part in r.Parts]

        # Filter by File
        file = request.args.get('file')
        if file:
            requests = [r for r in requests if file in r.File_IDs]

        # Filter by Created by
        created_by = request.args.get('created_by')
        if created_by:
            requests = [r for r in requests if r.Assigned_By == created_by]

        # Filter by Completed by
        completed_by = request.args.get('completed_by')
        if completed_by:
            requests = [r for r in requests if r.Completed_By == completed_by]

        # Filter by Requested by
        requested_by = request.args.get('requested_by')
        if requested_by:
            from flask import request, render_template
            from models import Maintenance

            # Function to filter maintenance requests
            def filter_requests(requests):
                # Filter by Requested By
                requested_by = request.args.get('requested_by')
                if requested_by:
                    requests = [r for r in requests if r.Requested_By == requested_by]

                # Filter by Additional worker
                additional_worker = request.args.get('additional_worker')
                if additional_worker:
                    requests = [r for r in requests if additional_worker in r.Additional_Workers]

                # Filter by Created Date
                created_date_start = request.args.get('created_date_start')
                created_date_end = request.args.get('created_date_end')
                if created_date_start and created_date_end:
                    requests = [r for r in requests if created_date_start <= r.Created_On <= created_date_end]

                # Filter by Completed Date
                completed_date_start = request.args.get('completed_date_start')
                completed_date_end = request.args.get('completed_date_end')
                if completed_date_start and completed_date_end:
                    requests = [r for r in requests if completed_date_start <= r.Completed_On <= completed_date_end]

                # Filter by Last Updated Date
                last_updated_date_start = request.args.get('last_updated_date_start')
                last_updated_date_end = request.args.get('last_updated_date_end')
                if last_updated_date_start and last_updated_date_end:
                    requests = [r for r in requests if last_updated_date_start <= r.Updated_On <= last_updated_date_end]

                # Filter by Location
                location = request.args.get('location')
                if location:
                    requests = [r for r in requests if r.Location_Name == location]

                # Filter by Status
                status = request.args.get('status')
                if status:
                    requests = [r for r in requests if r.Status == status]

                # Filter by Priority
                priority = request.args.get('priority')
                if priority:
                    requests = [r for r in requests if r.Priority == priority]

                # Filter by Bookmarked
                bookmarked = request.args.get('bookmarked')
                if bookmarked:
                    requests = [r for r in requests if r.Bookmarked]

                return requests


            # Route to display maintenance requests
            @app.route('/requests')
            def display_requests():
                # Retrieve all maintenance requests from the database
                requests = Maintenance.query.all()

                # Filter the requests based on the query parameters
                requests = filter_requests(requests)

                # Render the template with the requests data
                return render_template('requests.html', requests=requests)


            # Function to schedule preventive maintenance tasks
            def schedule_preventive_maintenance(asset_name, schedule_interval):
                # Create a new Maintenance object with the given asset name and repeating schedule
                maintenance = Maintenance(Asset_Name=asset_name, Repeating_Schedule=True)
                # Set the schedule interval for the maintenance task
                maintenance.Schedule_Interval = schedule_interval
                # Add the new maintenance task to the database
                db.session.add(maintenance)
                db.session.commit()


            # Function to generate a report of maintenance requests
            def generate_maintenance_report():
                # Retrieve all maintenance requests from the database
                requests = Maintenance.query.all()
                # Create a dictionary to store the count of requests by status
                status_counts = {}
                for request in requests:
                    status = request.Status
                    if status in status_counts:
                        status_counts[status] += 1
                    else:
                        status_counts[status] = 1
                # Create a dictionary to store the count of requests by category
                category_counts = {}
                for request in requests:
                    category = request.Category
                    if category in category_counts:
                        category_counts[category] += 1
                    else:
                        category_counts[category] = 1
                # Create a dictionary to store the count of requests by team assigned
                team_counts = {}
                for request in requests:
                    team = request.Team_Assigned
                    if team in team_counts:
                        team_counts[team] += 1
                    else:
                        team_counts[team] = 1
                # Create a dictionary to store the count of requests by asset name
                asset_counts = {}
                for request in requests:
                    asset = request.Asset_Name
                    if asset in asset_counts:
                        asset_counts[asset] += 1
                    else:
                        asset_counts[asset] = 1
                # Create a dictionary to store the count of requests by priority
                priority_counts = {}
                for request in requests:
                    priority = request.Priority
                    if priority in priority_counts:
                        priority_counts[priority] += 1
                    else:
                        priority_counts[priority] = 1
                # Create a dictionary to store the count of requests by location
                location_counts = {}
                for request in requests:
                    location = request.Location_Name
                    if location in location_counts:
                        location_counts[location] += 1
                    else:
                        location_counts[location] = 1
                # Return a dictionary containing all the counts
                return {
                    'status_counts': status_counts,
                    'category_counts': category_counts,
                    'team_counts': team_counts,
                    'asset_counts': asset_counts,
                    'priority_counts': priority_counts,
                    'location_counts': location_counts
                }
