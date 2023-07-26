from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from stl.mesh import Mesh
import os
import tempfile
import math
from scipy.optimize import minimize

quote = Blueprint('quote', __name__)

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
    material_to_thickness = {
        "Aluminum (AlSi10Mg)": 0.00011811,
        "Titanium Ti64": 0.00011811,
        "Stainless Steel 316L": 0.00015748,
        "Stainless Steel 17-4PH": 0.00015748,
        "Nickel Alloy 718": 0.00015748,
        "Nickel Alloy 625": 0.00015748,
        "Cobalt Chrome": 0.00015748
    }
    return material_to_thickness.get(material, 0)

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
        layer_thickness = calculate_layer_thickness(material)
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
            'LayerThickness': layer_thickness,
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
            'PackEfficiency': 20  # Set the default value of PackEfficiency to 20
        })
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))

    col_order = ['PartName', 'OrderQty', 'xExtents', 'yExtents', 'zExtents', 'Volume', 'SurfaceArea', 'Orientation',
                 'Material', 'LayerThickness', 'ProjectedArea', 'Diagonal', 'BuildHours', 'UnpackHours', 'NumBuilds',
                 'NewXExt', 'NewYExt', 'NewZExt', 'BuildQty', 'NumFullBuilds', 'RemQty', '[%BuildRem]',
                 'BuildRecTime', 'TFB_RecTime', 'PB_RecTime', 'ExpTime', 'TotalBuildTime']
    return pd.DataFrame(data, columns=col_order)

def get_user_input(name, index):
    return request.form.get(f"{name}_{index}", type=float)

def get_initial_coefficients():
    # You need to define your initial values for coeff_a, coeff_b, coeff_c, coeff_d, and intercept
    # Example:
    coeff_a = 0.1
    coeff_b = 0.2
    coeff_c = 0.3
    coeff_d = 0.4
    intercept = 0.5
    return coeff_a, coeff_b, coeff_c, coeff_d, intercept

def optimize_metrics(df, coeff_a, coeff_b, coeff_c, coeff_d, intercept):
    # Objective function for optimization
    def objective_function(coeffs):
        nonlocal coeff_a, coeff_b, coeff_c, coeff_d, intercept

        # Update the coefficients for this iteration
        coeff_a, coeff_b, coeff_c, coeff_d, intercept = coeffs

        # Calculate the estimated quantities based on the current coefficients
        estimated_qty = np.exp(coeff_a * np.log(df['OrderQty']) + coeff_b) - coeff_c * np.log(df['OrderQty']) - coeff_d * np.log(df['Diagonal']) + intercept

        # Calculate the error between estimated quantities and provided quantities
        error = np.sum((estimated_qty - df['OrderQty']) ** 2)

        return error

    # Initial guess for the coefficients
    initial_guess = np.array([coeff_a, coeff_b, coeff_c, coeff_d, intercept])

    # Optimization bounds for coefficients
    # You can adjust the bounds based on your knowledge of valid coefficient ranges
    bounds = ((-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100))

    # Perform the optimization to find the best-fit coefficients
    result = minimize(objective_function, initial_guess, bounds=bounds)

    # Update the coefficients with the optimized values
    coeff_a, coeff_b, coeff_c, coeff_d, intercept = result.x

    # Calculate the final NumBuilds and TotalBuildTime based on the optimized coefficients
    df['NumBuilds'] = np.ceil((df['OrderQty'] * (np.exp(coeff_a * np.log(df['OrderQty'] + 1)) + coeff_b) - np.exp(coeff_a * np.log(df['OrderQty']) + coeff_b) - df['TFB_RecTime']) / df['ExpTime'])
    df['TotalBuildTime'] = (df['NumFullBuilds'] * df['BuildRecTime'] + np.where((df['[%BuildRem]'] < df['PackEfficiency']),
                                                                             (df['ProjectedArea'] * df['RemQty']) / (df['BuildArea'] * df['PackEfficiency']) * df['BuildRecTime'],
                                                                             df['BuildRecTime']) + df['OrderQty'] * df['ExpTime']) / df['OrderQty']

    # Update the DataFrame with the optimized results
    session["results"] = df.to_dict(orient='records')

    return df, coeff_a, coeff_b, coeff_c, coeff_d, intercept

@quote.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

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
                results = calculate_metrics(stl_files)
                results = results.reset_index(drop=True)  # Drop the previous index and reset it
                # Set the default value of PackEfficiency to 20 for all rows
                results['PackEfficiency'] = 20
                # Set the default small frame machine as the build area 96.8751999504 = 9.84252 x 9.84252
                results['BuildArea'] = 96.8751999504

                session["results"] = results.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries
                return render_template("quote.html", user=current_user, results=results)

        elif 'update_quote' in request.form:
            results_data = session.get('results')
            if results_data is not None and len(results_data) > 0:
                df = pd.DataFrame(results_data)  # Convert list of dictionaries back to DataFrame

                # Retrieve the filenames from the DataFrame
                stl_files = df['PartName'].tolist()

                if not any(stl_files):  # Check if any STL files are selected
                    flash('Please select one or more files.', category='error')
                    return redirect(url_for('quote.quote_page'))

                user_inputs = {}
                for index, row in df.iterrows():
                    line_item = row['PartName']  # Use 'PartName' as the line item
                    user_inputs[line_item] = {
                        "OrderQty": request.form.get(f"order_qty_{index}", type=float),
                        "Orientation": request.form.get(f"orientation_{index}"),
                        "Material": request.form.get(f"material_{index}"),
                    }

                # Update DataFrame with user inputs
                df.update(pd.DataFrame.from_dict(user_inputs, orient='index'))
                df['ProjectedArea'] = df.apply(lambda row: calculate_projected_area(row['xExtents'], row['yExtents'], row['zExtents'], row['Orientation']), axis=1)
                df['Diagonal'] = df.apply(lambda row: calculate_diagonal(row['xExtents'], row['yExtents'], row['zExtents']), axis=1)
                df['LayerThickness'] = df['Material'].apply(calculate_layer_thickness)

                # Perform optimization to update coefficients and other metrics
            coeff_a, coeff_b, coeff_c, coeff_d, intercept = get_initial_coefficients()
            df, coeff_a, coeff_b, coeff_c, coeff_d, intercept = optimize_metrics(df, coeff_a, coeff_b, coeff_c, coeff_d, intercept)

            # Recalculate the values for Build Hours, Unpack Hours, and Num Builds
            df['BuildHours'] = df['NumBuilds'] * df['BuildRecTime']
            df['UnpackHours'] = df['OrderQty'] * df['ExpTime']
            df['NumBuilds'] = np.ceil((df['OrderQty'] * (np.exp(coeff_a * np.log(df['OrderQty'] + 1)) + coeff_b) - np.exp(coeff_a * np.log(df['OrderQty']) + coeff_b) - df['TFB_RecTime']) / df['ExpTime'])

            # Handle infinity values by setting them to a maximum integer value (e.g., 999)
            df['NumBuilds'] = df['NumBuilds'].replace(np.inf, 999).astype(int)

            # Set the 'Build Hours', 'Unpack Hours', and 'Num Builds' columns as strings to display them as labels
            df['BuildHours'] = df['BuildHours'].apply(lambda x: f"{x:.2f}")
            df['UnpackHours'] = df['UnpackHours'].apply(lambda x: f"{x:.2f}")
            
            
             # Convert 'BuildHours' and 'UnpackHours' to numeric
            df['BuildHours'] = pd.to_numeric(df['BuildHours'], errors='coerce')
            df['UnpackHours'] = pd.to_numeric(df['UnpackHours'], errors='coerce')

            df = df.reset_index(drop=True)  # Drop the previous index and reset it
            session["results"] = df.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries
            return render_template("quote.html", user=current_user, results=df)



    # Pass the existing DataFrame in the session to the template context if 'results' is available
    results_data = session.get('results')
    if results_data is not None and len(results_data) > 0:
        df = pd.DataFrame(results_data)
    else:
        df = pd.DataFrame()  # Create an empty DataFrame

    return render_template("quote.html", user=current_user, results=df)
