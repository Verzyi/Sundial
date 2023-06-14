from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import PowderBlends
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func

views = Blueprint('views', __name__)

numbers = []
weights = []
batchs = []
batchWeights = []


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
        
    if request.method == 'POST':
        if request.form.get('BlendNum') is not None:
            if len(request.form.get('BlendNum')) != 0:
                blendNumber = request.form.get('BlendNum')

                if int(request.form.get('BlendNum')) > 1:
                    search = PowderBlends.query.filter_by(PowderBlendID=blendNumber).all()

                    if search:
                        flash("Found blend number: " + str(blendNumber), category='success')
                        return render_template("searchBlends.html", user=current_user, blendNumber=search)
                    else:
                        flash("No blend found: " + str(blendNumber), category='error')
                        return redirect(url_for('views.searchBlends'))
                else:
                    flash("Blend number must be positive: " + str(blendNumber), category='error')
                    return redirect(url_for('views.searchBlends'))
                
    return render_template("searchBlends.html", user=current_user)


@views.route('/createBlend', methods=['GET', 'POST'])
@login_required
def create_blend():
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
                            # blendWeight= PowderBlends.query.filter_by(PowderBlendID= blendNumber).with_entities(PowderBlends.AddedWeight).first()
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
                            else:
                                flash("Blend number does not exist", category='error')

                        elif radioOption == 'Batch':
                            search = PowderBlends.query.filter_by(PowderInventoryBatchID=blendNumber).first()
                            blendWeight = PowderBlends.query(func.sum(PowderBlends)).filter_by(PowderBlendID=blendNumber).scalar()
                            if blendNumber in numbers:
                                flash("batch number is already added", category='error')
                            elif search:
                                if float(blendWeight.AddedWeight) < float(weight):
                                    flash("Blend cannot exceed the available weight (" + str(blendWeight.AddedWeight) + " Kg)", category='error')
                                else:
                                    flash("Blend entry added", category='success')
                                    batchs.append(blendNumber)
                                    batchWeights.append(weight)

                            else:
                                flash("Batch number does not exist", category='error')
                            

    


        elif 'create' in request.form:
            # blendMaterial = PowderBlends.query.filter_by(PowderBlendID=blendNumber).with_entities(PowderBlends.Material).first() need the table for this 
            blendMaterial = 'SS17-4'
            selectedMaterial = request.form.get('material')

            if numbers and blendMaterial == selectedMaterial:  #this will need to be change when its acutally looking at the database to blendMaterial.Material
                flash("Blend created", category='success')
                
                # Get the last PowderBlendID from the database
                last_blend = PowderBlends.query.order_by(PowderBlends.PowderBlendID.desc()).first()
                last_blend_id = last_blend.PowderBlendID if last_blend else 0

                last_id_blend = PowderBlends.query.order_by(PowderBlends.PowderBlendPartID.desc()).first()
                last_id = last_id_blend.PowderBlendID if last_id_blend else 0
                
                # Create a new instance of the PowderBlends model
                for x in range( len(numbers)):
                    new_blend = PowderBlends(
                    PowderBlendPartID=int(last_id + 1),
                    PowderBlendID=int(last_blend_id + 1),
                    OldPowderBlendID=int(numbers[x]),
                    AddedWeight=float(weights[x]),
                    DateAdded=datetime.now(),
                    PowderInventoryBatchID=None)  # Set this value accordingly  

                for x in range( len(batchs)):
                    new_blend = PowderBlends(
                    PowderBlendPartID =int(last_id + 1),
                    PowderBlendID=int(last_blend_id + 1),
                    OldPowderBlendID=None,
                    AddedWeight=float(batchWeights[x]),
                    DateAdded=datetime.now(),
                    PowderInventoryBatchID=batchs[x])  # Set this value accordingly  

                # Add the new_blend object to the database session
                db.session.add(new_blend)
                last_blend_id += 1
                last_id +=1

                db.session.commit()                

                # Reset the table of numbers and weights
                numbers.clear()
                weights.clear()
                batchs.clear()
            else:
                flash("Selected material does not match with the blend's material")

    return render_template("createBlend.html", user=current_user, numbers=numbers+batchs, weights=weights+batchWeights)






