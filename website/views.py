from flask import Blueprint, render_template, request, flash
from .models import PowderBlends
from . import db
from flask_login import login_user, login_required, current_user
from sqlalchemy.orm import Query, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select

engine = create_engine("sqlite:///:memory:", echo=True)
Base = declarative_base()
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

views = Blueprint('views',__name__)





@views.route('/')
@login_required
def home():
    return render_template("home.html", user = current_user)


@views.route('/blend', methods= ['GET','POST'])
@login_required
def blend():
	if request.method == 'POST':
		if request.form.get('BlendNum') is not None:

			if  len(request.form.get('BlendNum')) != 0: 
				blendNumber = request.form.get('BlendNum')
				if int(request.form.get('BlendNum')) > 1:

					

					#7362 good one to test
					search = PowderBlends.query.filter_by(PowderBlendID= blendNumber).all()


					if search:
						flash("found blend number", category='success')
						
					
						weight= PowderBlends.query.filter_by(PowderBlendID= blendNumber).with_entities(PowderBlends.AddedWeight).all()
						oldBlendNumber= PowderBlends.query.filter_by(PowderBlendID= blendNumber).with_entities(PowderBlends.OldPowderBlendID).all()
						lastWeight= PowderBlends.query.filter_by(PowderBlendID= blendNumber).with_entities(PowderBlends.AddedWeight).all()

						return render_template("blend.html", user = current_user, blendNumber = search)
						# return render_template("blend.html", user = current_user, blendNumber = search.PowderBlendID, weight = weight, oldBlendNumber = oldBlendNumber, lastWeight = lastWeight)

					else:
						flash("no blend found "+str(blendNumber), category='error')
						
				else:
					flash("Blend number Must be postive "+str(blendNumber), category='error')
					
			else:
				print("working on other")
		elif request.form.get('BlendNum') is not None or request.form.get('weight') is not None:
			if  len(request.form.get('BlendNum')) != 0: 
				blendNumber = request.form.get('BlendNum')
				if int(request.form.get('BlendNum')) > 1:
					search = PowderBlends.query.filter_by(PowderBlendID= blendNumber).all()

					if search:
						flash("found blend number", category='success')



	return render_template("blend.html", user = current_user)

@views.route('/builds')
@login_required
def builds():
    return render_template("home.html", user = current_user)