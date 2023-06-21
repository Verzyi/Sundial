from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import PowderBlends
from .models import Builds
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func
import socket
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    blends = PowderBlends.query.all()
    return render_template("home.html", user=current_user, blends=blends)


@views.route('/blend', methods=['GET', 'POST'])
@login_required
def blend():
    search = None
    numbers = []
    weights = []

    if request.method == 'POST':
        if request.form.get('BlendNum') is not None:
            if len(request.form.get('BlendNum')) != 0:
                blendNumber = request.form.get('BlendNum')

                if int(request.form.get('BlendNum')) > 1:
                    search = PowderBlends.query.filter_by(PowderBlendID=blendNumber).all()

                    if search:
                        flash("Found blend number: " + str(blendNumber), category='success')
                        return render_template("blend.html", user=current_user, blendNumber=search)
                    else:
                        flash("No blend found: " + str(blendNumber), category='error')
                        return redirect(url_for('views.blend'))
                else:
                    flash("Blend number must be positive: " + str(blendNumber), category='error')
                    return redirect(url_for('views.blend'))

        elif request.form.get('addBlendBtn') is not None:
            blendNumber = request.form.get('BlendNumber')
            weight = request.form.get('weight')

            if len(blendNumber) != 0 and len(weight) != 0:
                if int(weight) > 1:
                    numbers.append(blendNumber)
                    weights.append(weight)
                    flash("Blend added: " + str(blendNumber), category='success')

    return render_template("blend.html", user=current_user, blendNumber=search, numbers=numbers, weights=weights)




def print_sticker(printer_ip, blend_number, material, date, weight,qty):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the printer
    printer_address = (printer_ip, 9100)
    sock.connect(printer_address)

    # Send EPL commands to print the sticker
    commands = [
    "^XA",
    "^LL253",
    "^PW812",
    "^FO30,30",
    "^GB752,233,1,B,0",
    f"^FO40,90",  # Adjusted X and Y values for Blend ID text
    f"^A0N,26,19",  # Increased font size for Blend ID text
    f"^FDBlend ID: {blend_number}^FS",
    f"^FO40,120",  # Adjusted X and Y values for Material text
    f"^A0N,26,19",  # Increased font size for Material text
    f"^FDMaterial: {material}^FS",
    f"^FO40,150",  # Adjusted X and Y values for Weight text
    f"^A0N,26,19",  # Increased font size for Weight text
    f"^FDWeight: {weight}^FS",
    f"^FO40,180",  # Adjusted X and Y values for Date text
    f"^A0N,26,19",  # Increased font size for Date text
    f"^FDDate: {date}^FS",
    f"^FO260,90",  # Adjusted X and Y values for barcode (moved 0.8" to the left)
    f"^BY1.25,2.5,60",  # Adjusted barcode width, height, and darkness
    f"^B3N,N,100,Y,N",
    f"^FD{blend_number}^FS",
    # Copying elements starting at 2.1" from the left edge
    f"^FO460,90",
    f"^A0N,26,19",
    f"^FDBlend ID: {blend_number}^FS",
    f"^FO460,120",
    f"^A0N,26,19",
    f"^FDMaterial: {material}^FS",
    f"^FO460,150",
    f"^A0N,26,19",
    f"^FDWeight: {weight}^FS",
    f"^FO460,180",
    f"^A0N,26,19",
    f"^FDDate: {date}^FS",
    f"^FO680,90",
    f"^BY1.25,2.5,60",
    f"^B3N,N,100,Y,N",
    f"^FD{blend_number}^FS",
    f"^PQ{qty}",
    "^XZ"
    ]



    command_string = "\n".join(commands)
    sock.sendall(command_string.encode())

    # Close the socket
    sock.close()


@views.route('/searchBlends', methods=['GET', 'POST'])
@login_required
def searchBlends():
    search = None

    if request.method == 'POST':
        if 'search' in request.form:
            if request.form.get('BlendNum') is not None:
                if len(request.form.get('BlendNum')) != 0:
                    blendNumber = request.form.get('BlendNum')
                    session['last_blend_number'] = blendNumber  # Store the blend number in session

                    if int(request.form.get('BlendNum')) > 1:
                        search = PowderBlends.query.filter_by(PowderBlendID=blendNumber).all()

                        if search:
                            flash("Found blend number: " + str(blendNumber), category='success')
                        else:
                            flash("No blend found: " + str(blendNumber), category='error')
                    else:
                        flash("Blend number must be positive: " + str(blendNumber), category='error')

        elif 'Print' in request.form:
            printerName = request.form.get("printer")
            if printerName == 'Shop printer':
                printer_ip = '10.101.102.21'
            elif printerName == 'Programmers printer':
                printer_ip = '10.101.102.65'

                blend_number = session.get('last_blend_number')  # Retrieve the blend number from session

                if blend_number:
                    weight = db.session.query(func.sum(PowderBlends.AddedWeight)).filter(PowderBlends.PowderBlendID == blend_number).scalar()
                    date = PowderBlends.query.filter_by(PowderBlendID=blend_number).first()
                    date = date.DateAdded.strftime("%Y/%m/%d")
                    material = "SS17-4"  # Placeholder until I have a materials table
                    qty = request.form.get("qty")
                    # Print the sticker
                    print_sticker(printer_ip, blend_number, material, date, weight,qty)
                    flash("Blend printed: " + str(qty), category='success')
                else:
                    flash("Blend number not found in session", category='error')
            else:
                flash("Error: Blend not printed", category='error')

    return render_template("searchBlends.html", user=current_user, blendNumber=search)




numbers = []
weights = []
batchs = []
batchWeights = []
material=[]


@views.route('/createBlend', methods=['GET', 'POST'])
@login_required
def create_blend():

    blendOrBatch = 'Blend'

    if request.method == 'POST':
        blendNumber = request.form.get('BlendNumber')  # Move the assignment here

        if 'add' in request.form:
            blendNumber = request.form.get('BlendNumber')
            weight = request.form.get('weight')
            if blendNumber is not None and weight is not None:
                if len(blendNumber) != 0 and len(weight) != 0:
                    if float(weight) > 1:
                        radioOption = request.form.get('option')  # Get the selected radio button option
                        search = None
                        blendWeight = None

                        if radioOption == 'Blend':
                            search = PowderBlends.query.filter_by(PowderBlendID=blendNumber).first()
                            blendWeight = db.session.query(func.sum(PowderBlends.AddedWeight)).filter_by(PowderBlendID=blendNumber).scalar()
                            if blendNumber in numbers:
                                flash("Blend number is already added", category='error')
                            elif search:
                                if float(blendWeight) < float(weight):
                                    flash("Blend cannot exceed the available weight (" + str(blendWeight) + " Kg)", category='error')
                                else:
                                    flash("Blend entry added", category='success')
                                    numbers.append(blendNumber)
                                    weights.append(weight)
                                    material.append('SS17-4')
                            else:
                                flash("Blend number does not exist", category='error')

                        elif radioOption == 'Batch':
                            search = PowderBlends.query.filter_by(PowderInventoryBatchID=blendNumber).first()
                            blendWeight = db.session.query(func.sum(PowderBlends.AddedWeight)).filter_by(PowderBlendID=blendNumber).scalar()
                            if blendNumber in numbers:
                                flash("batch number is already added", category='error')
                            elif search:
                                if float(blendWeight) < float(weight):
                                    flash("Blend cannot exceed the available weight (" + str(blendWeight) + " Kg)", category='error')
                                else:
                                    flash("Blend entry added", category='success')
                                    batchs.append(blendNumber)
                                    batchWeights.append(weight)
                                    material.append('SS17-4')
                            else:
                                flash("Batch number does not exist", category='error')
                            

        elif 'create' in request.form:
            blendMaterial = 'SS17-4'
            selectedMaterial = request.form.get('material')

            if numbers and blendMaterial == selectedMaterial:
                flash("Blend created", category='success')

                last_blend = PowderBlends.query.order_by(PowderBlends.PowderBlendID.desc()).first()
                last_blend_id = last_blend.PowderBlendID if last_blend else 0

                last_id_blend = PowderBlends.query.order_by(PowderBlends.PowderBlendPartID.desc()).first()
                last_id = last_id_blend.PowderBlendID if last_id_blend else 0

                for x in range(len(numbers)):
                    new_blend = PowderBlends(
                        PowderBlendPartID=int(last_id + 1),
                        PowderBlendID=int(last_blend_id + 1),
                        OldPowderBlendID=int(numbers[x]),
                        AddedWeight=float(weights[x]),
                        DateAdded=datetime.now(),
                        PowderInventoryBatchID=None
                    )
                    db.session.add(new_blend)
                    last_id += 1

                for x in range(len(batchs)):
                    new_blend = PowderBlends(
                        PowderBlendPartID=int(last_id + 1),
                        PowderBlendID=int(last_blend_id + 1),
                        OldPowderBlendID=None,
                        AddedWeight=float(batchWeights[x]),
                        DateAdded=datetime.now(),
                        PowderInventoryBatchID=batchs[x]
                    )
                    db.session.add(new_blend)
                    last_id += 1

                db.session.commit()

                numbers.clear()
                weights.clear()
                batchs.clear()
                batchWeights.clear()
                material.clear()

            else:
                flash("Selected material does not match with the blend's material")

    return render_template("createBlend.html", user=current_user, blends=numbers, blendWeights=weights,
                           batchs=batchs, batchWeights=batchWeights, material=material,
                           totalWeight=sum([float(blendWeight) for blendWeight in weights] +
                                           [float(batchWeight) for batchWeight in batchWeights]),
                           type=blendOrBatch)


@views.route('/removeBlend/<int:blendIndex>', methods=['POST'])
@login_required
def remove_blend(blendIndex):
    if blendIndex < len(numbers):
        numbers.pop(blendIndex)
        weights.pop(blendIndex)
        material.pop(blendIndex)
    return redirect(url_for('views.create_blend'))




@views.route('/removeBatch/<int:batchIndex>', methods=['POST'])
@login_required
def remove_batch(batchIndex):
    if batchIndex < len(batchs):
        batchs.pop(batchIndex)
        batchWeights.pop(batchIndex)
        material.pop(batchIndex)
    return redirect(url_for('views.create_blend'))



@views.route('/createBatch', methods=['GET', 'POST'])
@login_required
def create_batch():
    return render_template("createBatch.html",user=current_user)





@views.route('/BlendHistory', methods=['GET', 'POST'])
@login_required
def blend_history():
    search = None
    query = PowderBlends.query.order_by(PowderBlends.DateAdded.desc())
    
    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            query = query.filter(PowderBlends.PowderBlendID.contains(search))

    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of rows to display per page
    blends = query.paginate(page=page, per_page=per_page)
    
    return render_template('blend_history.html',user=current_user, blends=blends, search=search)


# builds application
@views.route('/builds', methods=['GET', 'POST'])
@login_required
def builds():

    # current_blend = {
    #     'blend_id': '12345',
    #     'created_on': '2023-06-13',
    #     'created_by': 'John Doe'
    #     }
    # Handle GET request
    if request.method == 'GET':
        builds = Builds.query.all()
        return render_template('builds.html', user=current_user, builds=builds, current_build=None)

    # Handle POST request
    if request.method == 'POST':
        # Retrieve form data
        build_id = request.form.get('build_id')
        created_by = request.form.get('created_by')
        # Retrieve other form data

        # Create a new Build object and save it to the database
        new_build = Builds(build_id=build_id, created_by=created_by)
        db.session.add(new_build)
        db.session.commit()

    

        # Redirect to the builds page or display a success message
    return render_template('builds.html', user=current_user, current_build=None)



