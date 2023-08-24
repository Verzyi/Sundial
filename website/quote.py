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
    "Aluminum (AlSi10Mg)": {"CoeffA": 0.655, "CoeffB": 0.045, "CoeffC": 0.047, "CoeffD": 0.098, "Intercept": -0.471, "LayerThickness": 0.0011811 },
    "Titanium Ti64": {"CoeffA": 1.943, "CoeffB": 0.020, "CoeffC": -0.033, "CoeffD": 0.119, "Intercept": -0.283, "LayerThickness": 0.0011811 },
    "Stainless Steel 316L": {"CoeffA": 1.359, "CoeffB": 0.018, "CoeffC": 0.002, "CoeffD": 0.259, "Intercept": -0.244, "LayerThickness": 0.0015748},
    "Stainless Steel 17-4PH": {"CoeffA": 1.666, "CoeffB": 0.042, "CoeffC": -0.030, "CoeffD": 0.110, "Intercept": -0.099, "LayerThickness": 0.0015748},
    "Nickel Alloy 718": {"CoeffA": 1.608, "CoeffB": 0.025, "CoeffD": 0.298, "LayerThickness": 0.0015748},
    "Nickel Alloy 625": {"CoeffA": 1.212, "CoeffB": 0.048, "CoeffD": -0.006, "LayerThickness": 0.0015748},
    "Cobalt Chrome": {"CoeffA": 1.143, "CoeffB": 0.040, "CoeffC": 0.192, "CoeffD": 0.611, "Intercept": -1.405, "LayerThickness": 0.0015748},
}

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

        orientation = "Z"
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
            'NewXExt': x,
            'NewYExt': y,
            'NewZExt': z,
            'BuildQty': 0,
            'NumFullBuilds': 0,
            'RemQty': 0,
            '%BuildRem': 0,
            'BuildRecTime': 0,
            'TFB_RecTime': 0,
            'PB_RecTime': 0,
            'ExpTime': 0,
            'LayerThickness':0,
            'TotalBuildTime': 0,
            'LeadTime': 0,
            'PackEfficiency': 0.20,  # Set the default value of PackEfficiency to 20%
            'BuildArea': 81  # Set the default value of BuildArea to 81
        })
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))

    col_order = ['PartName', 'OrderQty', 'xExtents', 'yExtents', 'zExtents', 'Volume', 'SurfaceArea', 'Orientation',
                 'Material', 'LayerThickness', 'ProjectedArea', 'Diagonal', 'BuildHours', 'UnpackHours', 'NumBuilds',
                 'NewXExt', 'NewYExt', 'NewZExt', 'BuildQty', 'NumFullBuilds', 'RemQty', '%BuildRem', 'LeadTime',
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
    row['ProjectedArea'] = row['NewXExt'] * row['NewYExt']  # Update ProjectedArea calculation
    row['Diagonal'] = calculate_diagonal(row['NewXExt'], row['NewYExt'], row['NewZExt'])
    row ['LayerThickness']= material_info.get(material, {}).get("LayerThickness", 0)
    
    build_length = math.sqrt(row['BuildArea'])
    build_qty = (
    math.floor(build_length / row['NewXExt']) * math.floor(build_length / row['NewYExt']) +
    math.floor((build_length % row['NewYExt']) / row['NewXExt']) * math.floor(build_length / row['NewYExt']) +
    math.floor((build_length % row['NewXExt']) / row['NewYExt']) * math.floor(build_length / row['NewXExt'])
    )

    try:
        row['BuildQty'] = build_qty
        row['RemQty'] = row['OrderQty'] % row['BuildQty']
        row['BuildRem'] = (row['RemQty'] * row['ProjectedArea']) / row['BuildArea']
        row['NumFullBuilds'] = math.floor(row['OrderQty'] / row['BuildQty'])  # Calculate the number of full builds and round down
        row['NumBuilds'] = math.ceil(row['NumFullBuilds'] + row['BuildRem'])
        
        
        # Calculate NumBuilds and round up to the next whole number
        num_builds = math.ceil(row['NumBuilds']) if not math.isnan(row['NumBuilds']) and math.isfinite(row['NumBuilds']) else 0

        # Calculate the estimated quantity
        estimated_qty = math.exp(coeff_a * math.log(row['OrderQty'] + 1) + coeff_b * row['LayerThickness']) - coeff_c * math.log(row['OrderQty'] + 1) - coeff_d * row['Diagonal'] + intercept

        print(f"build_length: {build_length}")
        print(f"NewXExt: {row['NewXExt']}")
        print(f"NewYExt: {row['NewYExt']}")
        print(f"ProjectedArea: {row['ProjectedArea']}")
        print(f"Diagonal: {row['Diagonal']}")
        print(f"BuildQty: {row['BuildQty']}")
        print(f"BuildRem: {row['BuildRem']}")
        print(f"NumFullBuilds: {row['NumFullBuilds']}")
        print(f"NumBuilds: {row['NumBuilds']}")
        print(f"RemQty: {row['RemQty']}")
        print(f"Estimated Qty: {estimated_qty}")
        
        
        return row
    except Exception as e:
        print(f"Error calculating NumBuilds: {e}")
        return row

def calculate_exp_time(row):
    material = row['Material']
    material_coeffs = material_info.get(material, {})
    coeff_a = material_coeffs.get("CoeffA", 0)
    coeff_b = material_coeffs.get("CoeffB", 0)
    coeff_c = material_coeffs.get("CoeffC", 0)
    coeff_d = material_coeffs.get("CoeffD", 0)
    intercept = material_coeffs.get("Intercept", 0)
    row ['LayerThickness']= material_info.get(material, {}).get("LayerThickness", 0)

    exp_time = coeff_a * row['Volume'] + coeff_b * row['SurfaceArea'] + coeff_c * row['ProjectedArea'] + coeff_d * row['Diagonal'] + intercept

    # If the calculated exp_time is less than or equal to 0, set it to the minimum value 0.1
    if exp_time <= 0:
        exp_time = 0.1
        
    print(f"exp_time: {exp_time}")
    return exp_time

def calculate_P_Rem(row):
    p_rem = (row['RemQty'] * row['ProjectedArea']) / row['BuildArea'] 
    return p_rem

def calculate_build_rec_time(row):
    StockHeight = 5 / 25.4  # Convert StockHeight from mm to inches
    LayerTime = 0.00249441933310151
    material = row['Material']
    row['LayerThickness']= material_info.get(material, {}).get("LayerThickness", 0)
    build_rec_time = ((row['NewZExt'] + StockHeight) / row['LayerThickness']) * LayerTime
    return build_rec_time

def compute_linest(y_values, x_values):
    # Calculate the natural logarithm of the values
    ln_y = np.log(y_values)
    ln_x = np.log(x_values)

    # Use polyfit to calculate the linear regression parameters
    # Note: polyfit can be used to fit data with a polynomial, but in this case, we are using it to fit an exponential
    slope, intercept = np.polyfit(ln_x, ln_y, 1)
    
    return slope, intercept

def calculate_build_hours(row):
    qty = []
    for count in range(1, 11):
        build_qty = row['BuildQty']
        build_rec_time = row['BuildRecTime']
        projected_area = row['ProjectedArea']
        build_area = row['BuildArea']
        pack_efficiency = row['PackEfficiency']
        exp_time = row['ExpTime']
        order_qty = row["OrderQty"]        

        
        int_division = count // build_qty
        mod_division = count % build_qty

        part1 = int_division * build_rec_time

        if ((mod_division * projected_area) / build_area) < pack_efficiency:
            part2 = (projected_area * mod_division) / (build_area * pack_efficiency) * build_rec_time
        else:
            part2 = build_rec_time

        part3 = count * exp_time

        # Final equivalent of the formula
        build_hours = (part1 + part2 + part3) / count

        qty.append(build_hours)
        print(f"build_hours qty {count}: {build_hours}")
    slope, intercept = compute_linest(qty,list(range(1, 11)))
    print(slope, intercept)
    
    interceptPower = np.exp(intercept)
    
    build_hours = interceptPower * (order_qty ** slope)

    
    return build_hours

def part_build_time(row):
    PartBuildTime = row['TotalBuildTime'] / row['OrderQty']   
    return PartBuildTime

def tfb_recTime(row):
    tfb_recTime = row['NumFullBuilds']*row['BuildRecTime']   
    print(f"tfb_recTime: {tfb_recTime}") 
    return tfb_recTime

def pb_recTime(row):
    if row['%BuildRem'] < row['PackEfficiency']:
        pb_recTime = (row['ProjectedArea'] * row['RemQty']) / (row['BuildArea'] * row['PackEfficiency']) * row['BuildRecTime']
    else:
        pb_recTime = row['BuildRecTime']
    print(f"pb_recTime: {pb_recTime}")
    return pb_recTime

def calculate_UnpackHours(row):
    unpackHours = ((row['NumFullBuilds'] + row['%BuildRem']) / row['OrderQty']) 
    print(f"unpackHours: {unpackHours}")
    return unpackHours

def calculate_lead_time(row):   
    lead_time = row['TFB_RecTime'] + row['BuildRecTime'] + row['OrderQty'] * row['ExpTime']
    return lead_time
   
def calculate_total_build_time(row):
    total_build_time = row['TFB_RecTime'] + row['PB_RecTime'] + row['OrderQty'] * row['ExpTime']
    return total_build_time

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
                
                # Calculate the Numbuilds for each row
                df = df.apply(calculate_num_builds, axis=1)
                
                df = df.reset_index(drop=True)  # Drop the previous index and reset it

                # Set the default small frame machine as the build area 81 = 9x9
                df['BuildArea'] = 81

                session["results"] = df.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries
                
                return render_template("quote.html", user=current_user, results=df)

        # Inside the 'update_quote' section of the 'quote_page' function
        elif 'update_quote' in request.form:
            results_data = session.get('results')
            
            # session["results"] = df.to_dict(orient='records')
            if results_data is not None and len(results_data) > 0:
                for index, row in enumerate(results_data):
                    # row['PackEfficiency'] = float(request.form.get('packefficiency'))
                    # row['PackEfficiency'] = 0
                    line_item = row['PartName']  # Get the part name as the line item
                    row['OrderQty'] = int(request.form.get(f"order_qty_input_{index}", 1))  # Use default value 0 if not found
                    row['Orientation'] = request.form.get(f"orientation_{index}", 'Z') # Use default value Z if not found
                    row['Material'] = request.form.get(f"material_{index}", 'Aluminum (AlSi10Mg)')  # Use default value 'Aluminum (AlSi10Mg)' if not found in session
                    

                    # Calculate newXExt, newYExt, and newZExt based on orientation
                    if row['Orientation'] == 'X':
                        new_x, new_y, new_z = float(request.form.get(f"zExtents_{index}", 0)), float(request.form.get(f"yExtents_{index}", 0)), float(request.form.get(f"xExtents_{index}", 0))
                    elif row['Orientation'] == 'Y':
                        new_x, new_y, new_z = float(request.form.get(f"xExtents_{index}", 0)), float(request.form.get(f"zExtents_{index}", 0)), float(request.form.get(f"yExtents_{index}", 0))
                    elif row['Orientation'] == 'Z':
                        new_x, new_y, new_z = float(request.form.get(f"xExtents_{index}", 0)), float(request.form.get(f"yExtents_{index}", 0)), float(request.form.get(f"zExtents_{index}", 0))

                    row['NewXExt'], row['NewYExt'], row['NewZExt'] = new_x, new_y, new_z


                    # Update the values in the results_data list
                    results_data[index] = row
                    

                if row["BuildQty"] <= 0:
                    flash('Error with file.', category='error')
                else:
                    # Update the session with modified results_data
                    session["results"] = results_data
                    df = pd.DataFrame(results_data)  # Convert list of dictionaries back to DataFrame with modified values
                    
                    # Calculate the Numbuilds for each row
                    df = df.apply(calculate_num_builds, axis=1)
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the %rem for each row
                    df['%BuildRem'] = df.apply(calculate_P_Rem, axis=1)
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the BuildRecTime for each row
                    df['BuildRecTime'] = df.apply(calculate_build_rec_time, axis=1)
                    print(f"BuildRecTime: {df['BuildRecTime']}")
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the calculate_exp_time for each row
                    df['ExpTime'] = df.apply(calculate_exp_time, axis=1)
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the tfb_recTime for each row
                    df['TFB_RecTime'] = df.apply(tfb_recTime, axis=1)
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the pb_recTime for each row
                    df['PB_RecTime'] = df.apply(pb_recTime, axis=1)
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the Unpack Hours for each row
                    df['UnpackHours'] = df.apply(calculate_UnpackHours, axis=1)
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the BuildHours for each row (optional if you want to use it separately)
                    df['BuildHours'] = df.apply(calculate_build_hours, axis=1)
                    print(f"BuildHours: {df['BuildHours']}")
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the TotalBuildTime for each row
                    df['LeadTime'] = df.apply(calculate_lead_time, axis=1)
                    print(f"LeadTime: {df['LeadTime']}")
                    session["results"] = df.to_dict(orient='records')
                    
                    # Calculate the TotalBuildTime for each row
                    df['TotalBuildTime'] = df.apply(calculate_total_build_time, axis=1)
                    print(f"TotalBuildTime: {df['TotalBuildTime']}")
                    session["results"] = df.to_dict(orient='records')
                    
                    
                    
                    

                    return render_template("quote.html", user=current_user, results=df)




    # Pass the existing DataFrame in the session to the template context if 'results' is available
    results_data = session.get('results')
    if results_data is not None and len(results_data) > 0:
        df = pd.DataFrame(results_data)
    else:
        df = pd.DataFrame()  # Create an empty DataFrame

    return render_template("quote.html", user=current_user, results=df)
