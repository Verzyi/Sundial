from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import pandas as pd
from stl.mesh import Mesh
import os
import tempfile
from werkzeug.utils import secure_filename

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
    return Mesh.from_file(file_path)

def get_xyz(obj):
    x_ext = abs(obj.x.max() - obj.x.min())
    y_ext = abs(obj.y.max() - obj.y.min())
    z_ext = abs(obj.z.max() - obj.z.min())
    return x_ext, y_ext, z_ext

def get_properties(obj):
    vol, _, _ = obj.get_mass_properties()
    obj.update_areas()
    surface = obj.areas.sum()
    return vol, surface

def calculate_metrics(files):
    data = []
    for file_key, file in files.items():
        if file:
            file_path = save_temp_file(file)  # Save the file to a temporary location
            obj = get_mesh(file_path)  # Load the STL mesh from the temporary file
            x, y, z = get_xyz(obj)
            vol, surface = get_properties(obj)
            data.append({
                'PartName': os.path.basename(file.filename),
                'OrderQty': 1,
                'xExtents': x,
                'yExtents': y,
                'zExtents': z,
                'Volume': vol,
                'SurfaceArea': surface
            })
            os.remove(file_path)  # Remove the temporary file
            os.rmdir(os.path.dirname(file_path))  # Remove the temporary folder

    return pd.DataFrame(data)

@quote.route('/Quote', methods=['GET', 'POST'])
@login_required
def quote_page():
    if request.method == 'POST':
        stl_files = request.files
        if not bool(stl_files):  # Check if no files were selected
            flash('No STL files selected.', category='error')
            return redirect(url_for('quote.Quote'))

        # Process the STL files and calculate the quote
        results = calculate_metrics(stl_files)

        if results is not None and not results.empty:  # Check if the DataFrame is not empty
            return render_template("quote.html", user=current_user, results=results)

        flash('Error occurred during quote calculation.', category='error')
        return redirect(url_for('quote.Quote'))

    return render_template("quote.html", user=current_user)
