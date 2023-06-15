from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import PowderBlends
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func

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



@views.route('/builds')
@login_required
def builds():
    return render_template("home.html", user=current_user)




@views.route('/searchBlends' , methods=['GET', 'POST'])
@login_required
def searchBlends():
    search = None   
    if request.method == 'POST':
        if 'search' in request.form:
            if request.form.get('BlendNum') is not None:
                if len(request.form.get('BlendNum')) != 0:
                    blendNumber = request.form.get('BlendNum')

                    if int(request.form.get('BlendNum')) > 1:
                        search = PowderBlends.query.filter_by(PowderBlendID=blendNumber).all()

                        if search:
                            flash("Found blend number: " + str(blendNumber), category='success')
    
                        else:
                            flash("No blend found: " + str(blendNumber), category='error')
                        
                    else:
                        flash("Blend number must be positive: " + str(blendNumber), category='error')
                    
        
        elif 'print' in request.form:
           
            blendID = search.PowderBlendID
            weight = search.AddedWeight
            # Print the sticker
            print_sticker(blendID, weight)
            flash("Blend printed: " + str(blendNumber), category='success')
            


    return render_template("searchBlends.html", user=current_user,blendNumber=search)

def print_sticker(blendID, weight):
    printer_ip = "10.101.102.65"
    label_width = "1.25"

    # Connect to the printer and send the print command
    # You may need to use a library or SDK specific to your printer model
    # Consult the printer's documentation for the correct implementation

    # Example code using the requests library
    import requests

    url = f"http://{printer_ip}/print"
    content = f"Blend ID: {blendID}\nWeight: {weight}"
    params = {
        "content": content,
        "labelWidth": label_width
    }

    response = requests.get(url, params=params)

    # Handle the response as per your requirement
    # For example, check the response status code

    if response.status_code == 200:
        print("Sticker printed successfully")
    else:
        print("Failed to print sticker")


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



