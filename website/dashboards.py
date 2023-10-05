from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask_bcrypt import Bcrypt
from . import db
from .mpd_dash import mpd_dash
import pandas as pd
from sqlalchemy import func

# Create a Blueprint for your views
dashboards_bp = Blueprint('dashboards_bp', __name__)
bcrypt = Bcrypt()


@dashboards_bp.route('/printers')
@login_required
def PrinterDash():
    try:
        from .models_status import StatusTable
        from .models_status import db

        # Get the latest status for each machine
        latest_statuses = db.session.query(StatusTable).distinct(StatusTable.machine).group_by(StatusTable.machine).order_by(StatusTable.timestamp.desc()).first()
        
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

        # Create a list to store data for each machine
        machine_data = []

        # Loop through machines and get the latest data for each machine
        for machine in machines_mapping:
            si_number = machines_mapping.get(machine, None)
            if si_number:
                latest_data = db.session.query(StatusTable).filter_by(machine=si_number).order_by(StatusTable.timestamp.desc()).first()
                print(latest_data)
                if latest_data:
                    machine_data.append({
                        'Alias': machine,
                        'Si Number': f"Si{latest_data.machine}",
                        'Status': latest_data.status if latest_data.status else '',
                        # Add other columns as needed from latest_data
                    })
                else:
                    machine_data.append({
                        'Alias': machine,
                        'Si Number': f"Si{si_number}",
                        'Status': 'N/A',  # Or any other default value to indicate no data
                        # Add other columns as needed with default values
                    })
        # Create a DataFrame from the machine data
        df = pd.DataFrame(machine_data)

        # Print the DataFrame for debugging
        print(df)

        # Pass the DataFrame to the template
        return render_template('dashboards/printers.html', user=current_user, machine_return=df)

    except Exception as e:
        # Log connection error or other exceptions
        app.logger.error(f"An error occurred: {e}")
        return render_template('dashboards/printers.html', user=current_user)