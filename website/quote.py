from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
import tempfile
import math
from stl.mesh import Mesh

quote = Blueprint('quote', __name__)

# Material information with constants for different materials
material_info = {
    "Aluminum (AlSi10Mg)": {"CoeffA": 0.655, "CoeffB": 0.045, "CoeffC": 0.047, "CoeffD": 0.098, "Intercept": -0.471, "LayerThickness": 0.001},
    "Titanium Ti64": {"CoeffA": 1.943, "CoeffB": 0.020, "CoeffC": -0.033, "CoeffD": 0.119, "Intercept": -0.283, "LayerThickness": 0.001},
    "Stainless Steel 316L": {"CoeffA": 1.359, "CoeffB": 0.018, "CoeffC": 0.002, "CoeffD": 0.259, "Intercept": -0.244, "LayerThickness": 0.002},
    "Stainless Steel 17-4PH": {"CoeffA": 1.666, "CoeffB": 0.042, "CoeffC": -0.030, "CoeffD": 0.110, "Intercept": -0.099, "LayerThickness": 0.002},
    "Nickel Alloy 718": {"CoeffA": 1.608, "CoeffB": 0.025, "CoeffD": 0.298, "LayerThickness": 0.002},
    "Nickel Alloy 625": {"CoeffA": 1.212, "CoeffB": 0.048, "CoeffD": -0.006, "LayerThickness": 0.002},
    "Cobalt Chrome": {"CoeffA": 1.143, "CoeffB": 0.040, "CoeffC": 0.192, "CoeffD": 0.611, "Intercept": -1.405, "LayerThickness": 0.002},
}


BuildLength = 9.0
BuildArea = 81.00


def save_temp_file(file):
    temp_folder = tempfile.mkdtemp()  # Create a temporary folder
    filename = secure_filename(file.filename)
    file_path = os.path.join(temp_folder, filename)
    file.save(file_path)  # Save the file to the temporary folder
    return file_path


def get_mesh(file_path):
    try:
        return Mesh.from_file(file_path)
    except Exception as e:
        print(f"Error reading STL file: {e}")
        return None


def get_xyz(obj):
    x_ext = abs(obj.x.max() - obj.x.min())
    y_ext = abs(obj.y.max() - obj.y.min())
    z_ext = abs(obj.z.max() - obj.z.min())
    return x_ext, y_ext, z_ext


def get_properties(obj):
    vol, cog, inertia = obj.get_mass_properties()
    obj.update_areas()
    surface = obj.areas.sum()
    return vol, surface


def calculate_layer_thickness(material):
    return material_info[material].get("LayerThickness", 0)


def calculate_projected_area(x_extents, y_extents, z_extents, orientation):
    if orientation == "X":
        return y_extents * z_extents
    elif orientation == "Y":
        return z_extents * x_extents
    elif orientation == "Z":
        return x_extents * y_extents
    else:
        return 0


def calculate_diagonal(x_extents, y_extents, z_extents):
    return math.sqrt(x_extents**2 + y_extents**2 + z_extents**2)


def calculate_metrics(files):
    data = []
    for file in files:
        file_path = save_temp_file(file)
        obj = get_mesh(file_path)
        if obj is None:
            print(f"Skipping file: {file.filename} - Error reading STL file.")
            os.remove(file_path)
            os.rmdir(os.path.dirname(file_path))
            continue

        x, y, z = get_xyz(obj)
        vol, surface = get_properties(obj)

        orientation = "X"
        material = "Aluminum (AlSi10Mg)"
        projected_area = calculate_projected_area(x, y, z, orientation)
        diagonal = calculate_diagonal(x, y, z)

        data.append({
            'PartName': os.path.basename(file.filename),
            'OrderQty': 1,
            'xExtents': x,
            'yExtents': y,
            'zExtents': z,
            'Volume': vol,
            'SurfaceArea': surface,
            'Orientation': orientation,
            'Material': material,
            'ProjectedArea': projected_area,
            'Diagonal': diagonal,
            'BuildHours': 0,
            'UnpackHours': 0,
            'NumBuilds': 0,
            'NewXExt': 0,
            'NewYExt': 0,
            'NewZExt': 0,
            'BuildQty': 0,
            'NumFullBuilds': 0,
            'RemQty': 0,
            '[%BuildRem]': 0,
            'BuildRecTime': 0,
            'TFB_RecTime': 0,
            'PB_RecTime': 0,
            'ExpTime': 0,
            'TotalBuildTime': 0,
            'PackEfficiency': 0.20,  # Set the default value of PackEfficiency to 20%
            'BuildArea': 81  # Set the default value of BuildArea to 81
        })
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))

    col_order = ['PartName', 'OrderQty', 'xExtents', 'yExtents', 'zExtents', 'Volume', 'SurfaceArea', 'Orientation',
                 'Material', 'ProjectedArea', 'Diagonal', 'BuildHours', 'UnpackHours', 'NumBuilds',
                 'NewXExt', 'NewYExt', 'NewZExt', 'BuildQty', 'NumFullBuilds', 'RemQty', '[%BuildRem]',
                 'BuildRecTime', 'TFB_RecTime', 'PB_RecTime', 'ExpTime', 'TotalBuildTime', 'PackEfficiency', 'BuildArea']
    return pd.DataFrame(data, columns=col_order)

def calculate_num_builds(row):
    material = row['Material']
    coeff_a = material_info.get(material, {}).get("CoeffA", 0)
    coeff_b = material_info.get(material, {}).get("CoeffB", 0)
    coeff_c = material_info.get(material, {}).get("CoeffC", 0)
    coeff_d = material_info.get(material, {}).get("CoeffD", 0)
    intercept = material_info.get(material, {}).get("Intercept", 0)

    # Update user-specific variables based on the user input
    row['ProjectedArea'] = calculate_projected_area(row['NewXExt'], row['NewYExt'], row['NewZExt'], row['Orientation'])
    row['Diagonal'] = calculate_diagonal(row['NewXExt'], row['NewYExt'], row['NewZExt'])
    row['LayerThickness'] = calculate_layer_thickness(material)

    try:
        # Calculate TFB_RecTime and PB_RecTime based on other values in the row
        row['TFB_RecTime'] = row['NumFullBuilds'] * row['BuildRecTime']
        if row['[%BuildRem]'] < row['PackEfficiency']:
            row['PB_RecTime'] = (row['ProjectedArea'] * row['RemQty']) / (row['BuildArea'] * row['PackEfficiency']) * row['BuildRecTime']
        else:
            row['PB_RecTime'] = row['BuildRecTime']

        # Calculate the estimated quantity and number of builds
        estimated_qty = np.exp(coeff_a * np.log(row['OrderQty'] + 1) + coeff_b * row['LayerThickness']) - coeff_c * np.log(row['OrderQty'] + 1) - coeff_d * np.log(row['Diagonal']) + intercept
        num_builds = np.ceil(row['NumFullBuilds'] + row['[%BuildRem]'])

        print(num_builds)

        return int(num_builds) if not np.isnan(num_builds) and np.isfinite(num_builds) else 0
    except Exception as e:
        print(f"Error calculating NumBuilds: {e}")
        return 0



@quote.route('/Quote', methods=['GET', 'POST'])
@login_required
def quote_page():
    if request.method == 'POST':
        if 'makeQuote' in request.form:
            stl_files = request.files.getlist('stl_files')
            if not stl_files:
                flash('No STL files selected.', category='error')
                return redirect(url_for('quote.quote_page'))
            else:
                # Calculate the initial metrics without user inputs
                df = calculate_metrics(stl_files)
                df = df.reset_index(drop=True)  # Drop the previous index and reset it
                # Set the default value of PackEfficiency to 20% for all rows
                df['PackEfficiency'] = 0.20  # 20%
                # Set the default small frame machine as the build area 81 = 9x9
                df['BuildArea'] = 81

                session["results"] = df.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries
                return render_template("quote.html", user=current_user, results=df)

        # Inside the 'update_quote' section of the 'quote_page' function
        elif 'update_quote' in request.form:
            results_data = session.get('results')
            if results_data is not None and len(results_data) > 0:
                for index, row in enumerate(results_data):
                    line_item = row['PartName']  # Get the part name as the line item
                    row['OrderQty'] = float(request.form.get(f"order_qty_input_{line_item}", 1))  # Use default value 0 if not found
                    row['Orientation'] = request.form.get(f"orientation_{line_item}", 'X')
                    row['Material'] = request.form.get(f"material_{line_item}", 'Aluminum (AlSi10Mg)')  # Use default value 'Aluminum (AlSi10Mg)' if not found in session

                    # Calculate newXExt, newYExt, and newZExt based on orientation
                    if row['Orientation'] == 'X':
                        row['NewXExt'] = float(request.form.get(f"zExtents_{index}", 0))
                        row['NewYExt'] = float(request.form.get(f"yExtents_{index}", 0))
                        row['NewZExt'] = float(request.form.get(f"xExtents_{index}", 0))
                    elif row['Orientation'] == 'Y':
                        row['NewZExt'] = float(request.form.get(f"xExtents_{index}", 0))
                        row['NewXExt'] = float(request.form.get(f"zExtents_{index}", 0))
                        row['NewYExt'] = float(request.form.get(f"yExtents_{index}", 0))
                    elif row['Orientation'] == 'Z':
                        row['NewZExt'] = float(request.form.get(f"xExtents_{index}", 0))
                        row['NewYExt'] = float(request.form.get(f"yExtents_{index}", 0))
                        row['NewXExt'] = float(request.form.get(f"zExtents_{index}", 0))


                                        # Update the values in the results_data list
                    results_data[index] = row
                    


                # Update the session with modified results_data
                session["results"] = results_data
                df = pd.DataFrame(results_data)  # Convert list of dictionaries back to DataFrame with modified values
                df['NumBuilds'] = df.apply(calculate_num_builds, axis=1)

                return render_template("quote.html", user=current_user, results=df)




    # Pass the existing DataFrame in the session to the template context if 'results' is available
    results_data = session.get('results')
    if results_data is not None and len(results_data) > 0:
        df = pd.DataFrame(results_data)
    else:
        df = pd.DataFrame()  # Create an empty DataFrame

    return render_template("quote.html", user=current_user, results=df)
