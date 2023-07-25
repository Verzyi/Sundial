from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import pandas as pd
from stl.mesh import Mesh
import os
import tempfile
from werkzeug.utils import secure_filename
import math

quote = Blueprint('quote', __name__)

@quote.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

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
    # Placeholder function to calculate layer thickness based on the material
    # You can use a dictionary to map materials to their respective layer thickness values
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
    # Placeholder function to calculate the projected area based on orientation
    if orientation == "X":
        return y_extents * z_extents
    elif orientation == "Y":
        return z_extents * x_extents
    elif orientation == "Z":
        return x_extents * y_extents
    else:
        return 0

def calculate_diagonal(x_extents, y_extents, z_extents):
    # Placeholder function to calculate the diagonal of the part
    return math.sqrt(x_extents**2 + y_extents**2 + z_extents**2)

def calculate_metrics(files):
    data = []
    for file in files:
        file_path = save_temp_file(file)  # Save the file to a temporary location
        obj = get_mesh(file_path)  # Load the STL mesh from the temporary file
        if obj is None:
            print(f"Skipping file: {file.filename} - Error reading STL file.")
            os.remove(file_path)  # Remove the temporary file
            os.rmdir(os.path.dirname(file_path))  # Remove the temporary folder
            continue
        
        x, y, z = get_xyz(obj)
        vol, surface = get_properties(obj)

        # Perform additional calculations
        orientation = "X"  # You can modify this based on your requirements
        material = "Aluminum (AlSi10Mg)"  # You can modify this based on your requirements
        layer_thickness = calculate_layer_thickness(material)
        projected_area = calculate_projected_area(x, y, z, orientation)
        diagonal = calculate_diagonal(x, y, z)

        # Add the calculated values to the data list
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
            'Diagonal': diagonal
        })
        os.remove(file_path)  # Remove the temporary file
        os.rmdir(os.path.dirname(file_path))  # Remove the temporary folder

    col_order = ['PartName', 'OrderQty', 'xExtents', 'yExtents', 'zExtents', 'Volume', 'SurfaceArea', 'Orientation',
                 'Material', 'LayerThickness', 'ProjectedArea', 'Diagonal']
    return pd.DataFrame(data, columns=col_order)


def calculate_metrics_with_user_inputs(files, user_inputs):
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
        layer_thickness = calculate_layer_thickness(user_inputs[file.filename]["Material"])
        projected_area = calculate_projected_area(x, y, z, user_inputs[file.filename]["Orientation"])

        build_hours = user_inputs[file.filename].get("BuildHours", 0)
        unpack_hours = user_inputs[file.filename].get("UnpackHours", 0)
        num_builds = user_inputs[file.filename].get("NumBuilds", 0)

        data.append({
            'LineItem': file.filename,
            'OrderQty': 1,
            'PartName': os.path.basename(file.filename),
            'xExtents': x,
            'yExtents': y,
            'zExtents': z,
            'Volume': vol,
            'SurfaceArea': surface,
            'Orientation': user_inputs[file.filename]["Orientation"],
            'Material': user_inputs[file.filename]["Material"],
            'LayerThickness': layer_thickness,
            'ProjectedArea': projected_area,
            'BuildHours': build_hours,
            'UnpackHours': unpack_hours,
            'NumBuilds': num_builds
        })

        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))

    col_order = ['LineItem', 'PartName', 'OrderQty', 'xExtents', 'yExtents', 'zExtents', 'Volume', 'SurfaceArea',
                 'Orientation', 'Material', 'LayerThickness', 'ProjectedArea', 'BuildHours', 'UnpackHours', 'NumBuilds']
    return pd.DataFrame(data, columns=col_order)


@quote.route('/Quote', methods=['GET', 'POST'])
@login_required
def quote_page():
    if request.method == 'POST':
        stl_files = request.files.getlist('stl_files')
        if not stl_files:
            flash('No STL files selected.', category='error')
            return redirect(url_for('quote.quote_page'))

        # Calculate the initial metrics without user inputs
        results = calculate_metrics(stl_files)

        if results is not None and not results.empty:
            if 'update_quote' in request.form:
                user_inputs = {}
                for row in results.iterrows():
                    line_item = row[1]['LineItem']
                    user_inputs[line_item] = {
                        "OrderQty": request.form[f"order_qty_{line_item}"],
                        "Orientation": request.form[f"orientation_{line_item}"],
                        "Material": request.form[f"material_{line_item}"],
                        "BuildHours": request.form[f"build_hours_{line_item}"],
                        "UnpackHours": request.form[f"unpack_hours_{line_item}"],
                        "NumBuilds": request.form[f"num_builds_{line_item}"]
                    }

                # Recalculate metrics with user inputs
                updated_results = calculate_metrics_with_user_inputs(stl_files, user_inputs)
                updated_results = pd.merge(results, updated_results, on='LineItem', suffixes=('', '_updated'))
                results = updated_results.drop(columns=[col for col in updated_results.columns if '_updated' in col])

            return render_template("quote.html", user=current_user, results=results)

        flash('Error occurred during quote calculation.', category='error')
        return redirect(url_for('quote.quote_page'))

    # If the request method is GET, render the template with an empty DataFrame for results
    return render_template("quote.html", user=current_user, results=pd.DataFrame())