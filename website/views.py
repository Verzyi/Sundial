from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import PowderBlends
from . import db
from flask_login import login_user, login_required, current_user

views = Blueprint('views', __name__)

numbers = []
weights = []


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
        blendNumber = request.form.getlist('BlendNumber[]')
        weight = request.form.getlist('weight[]')

        for i in range(len(blendNumber)):
            current_blend_number = blendNumber[i]
            current_weight = weight[i]

            if current_blend_number and current_weight:
                if len(current_blend_number) != 0 and len(current_weight) != 0:
                    if int(current_weight) > 1:
                        search = PowderBlends.query.filter_by(PowderBlendID=current_blend_number).first()

                        if search:
                            flash("Found blend number: " + str(current_blend_number), category='success')
                            numbers.append(current_blend_number)
                            weights.append(current_weight)

    return render_template("createBlend.html", user=current_user, numbers=numbers, weights=weights)



