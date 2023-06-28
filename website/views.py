from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func, join
import socket
from datetime import datetime
from .blend_calculator import BlendDatabaseUpdater, PowderBlendCalc

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    blends = PowderBlends.query.all()
    return render_template("home.html", user=current_user, blends=blends)


@views.route('/blend', methods=['GET', 'POST'])
@login_required
def blend():

    return render_template("blend.html", user=current_user)


def print_sticker(printer_ip, blend_number, material, date, weight, qty):
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
        # Adjusted X and Y values for barcode (moved 0.8" to the left)
        f"^FO260,90",
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
                    # Store the blend number in session
                    session['last_blend_number'] = blendNumber

                    if int(request.form.get('BlendNum')) > 1:
                        # search = PowderBlends.query.filter_by(BlendID=blendNumber).all()

                        search = db.session.query(PowderBlends, MaterialsTable.MaterialName) \
                            .join(MaterialsTable, PowderBlends.MaterialID == MaterialsTable.MaterialID) \
                            .filter(PowderBlends.BlendID == blendNumber) \
                            .all()

                        if search:
                            flash("Found blend number: " +
                                  str(blendNumber), category='success')
                        else:
                            flash("No blend found: " +
                                  str(blendNumber), category='error')
                    else:
                        flash("Blend number must be positive: " +
                              str(blendNumber), category='error')

        elif 'Report' in request.form:
            flash("Making reports", category='success')
            # Retrieve the blend number from session
            blend_number = session.get('last_blend_number')
            if blend_number:
                blend_report = BlendReport(blend=blend_number)
                blend_report.load_data()
                blend_report.process_blend()
                report_html = blend_report.generate_report_pdf()  # Generate the report HTML
                return report_html  # Return the report HTML to be rendered in the browser

        elif 'Print' in request.form:
            printerName = request.form.get("printer")
            if printerName == 'Shop printer':
                printer_ip = '10.101.102.21'
            elif printerName == 'Programmers printer':
                printer_ip = '10.101.102.65'

                # Retrieve the blend number from session
                blend_number = session.get('last_blend_number')

                if blend_number:
                    search = db.session.query(PowderBlends, MaterialsTable.MaterialName) \
                        .join(MaterialsTable, PowderBlends.MaterialID == MaterialsTable.MaterialID) \
                        .filter(PowderBlends.BlendID == blend_number) \
                        .all()

                    if search:
                        for blend, material_name in search:
                            weight = blend.TotalWeight
                            date = blend.BlendDate
                            material = material_name
                            qty = request.form.get("qty")
                            # Print the sticker
                            print_sticker(printer_ip, blend_number,
                                          material, date, weight, qty)
                        flash("Blend printed: " + str(qty), category='success')
                    else:
                        flash("No blend found: " +
                              str(blend_number), category='error')
                else:
                    flash("Blend number not found in session", category='error')
            else:
                flash("Error: Blend not printed", category='error')

    return render_template("searchBlends.html", user=current_user, blends=search)


numbers = []
weights = []
batchs = []
batchWeights = []
materials = []


@views.route('/createBlend', methods=['GET', 'POST'])
@login_required
def create_blend():

    blendOrBatch = 'Blend'
    # material=db.session.query(MaterialsTable.MaterialName)

    if request.method == 'POST':
        blendNumber = request.form.get(
            'BlendNumber')  # Move the assignment here

        if 'add' in request.form:
            blendNumber = request.form.get('BlendNumber')
            weight = request.form.get('weight')
            if blendNumber is not None and weight is not None:
                if len(blendNumber) != 0 and len(weight) != 0:
                    if float(weight) > 1:
                        # Get the selected radio button option
                        radioOption = request.form.get('option')
                        search = None
                        blendWeight = None

                        if radioOption == 'Blend':
                            search = PowderBlends.query.filter_by(
                                BlendID=blendNumber).first()
                            if blendNumber in numbers:
                                flash("Blend number is already added",
                                      category='error')
                            elif search:
                                blendWeight = search.TotalWeight
                                material_id = search.MaterialID
                                # Join operation to retrieve MaterialName
                                query = db.session.query(MaterialsTable.MaterialName).join(
                                    PowderBlends, MaterialsTable.MaterialID == PowderBlends.MaterialID
                                ).filter(PowderBlends.MaterialID == material_id)

                                # Retrieve the MaterialName
                                material = query.first()[0]

                                if float(blendWeight) < float(weight):
                                    flash("Blend cannot exceed the available weight (" +
                                          str(blendWeight) + " Kg)", category='error')
                                else:
                                    flash("Blend entry added",
                                          category='success')
                                    numbers.append(blendNumber)
                                    weights.append(weight)
                                    materials.append(material)
                                    session['material_name'] = material
                            else:
                                flash("Blend number does not exist",
                                      category='error')

                        elif radioOption == 'Batch':
                            search = InventoryVirginBatch.query.filter_by(
                                BatchID=blendNumber).scalar()
                            if blendNumber in numbers:
                                flash("batch number is already added",
                                      category='error')
                            elif search:
                                batchWeight = search.VirginQty
                                if float(batchWeight) < float(weight):
                                    flash("Batch cannot exceed the available weight (" +
                                          str(blendWeight) + " Kg)", category='error')
                                else:
                                    flash("Blend entry added",
                                          category='success')
                                    batchs.append(blendNumber)
                                    batchWeights.append(weight)
                                    material_id = search.ProductID
                                    query = db.session.query(MaterialsTable.MaterialName).join(
                                        InventoryVirginBatch, MaterialsTable.ProductID == InventoryVirginBatch.ProductID
                                    ).filter(InventoryVirginBatch.ProductID == material_id)

                                    # Retrieve the MaterialName
                                    material = query.first()[0]

                                    materials.append(material)
                            else:
                                flash("Batch number does not exist",
                                      category='error')

        elif 'create' in request.form:
            if materials == []:
                flash("No items to Blend", category='error')

            # Check if all elements in the list are the same
            elif all(x == materials[0] for x in materials):
                # Retrieve the last material from session
                material_name = session.get('material_name')
                material = MaterialsTable.query.filter_by(
                    MaterialName=material_name).first()
                material_id = material.ProductID

                # update powderBlend records
                last_blend = PowderBlends.query.order_by(
                    PowderBlends.BlendID.desc()).first()
                last_blend_id = last_blend.BlendID if last_blend else 0

                new_blend = PowderBlends(
                    BlendID=int(last_blend_id + 1),
                    BlendDate=datetime.now().strftime("%m/%d/%Y %H:%M").lstrip("0").replace(" 0", " "),
                    BlendCreatedBy=current_user.id,
                    MaterialID=material_id,
                    TotalWeight=sum([float(blendWeight) for blendWeight in weights] +
                                    [float(batchWeight) for batchWeight in batchWeights])
                )
                db.session.add(new_blend)
                db.session.commit()

                flash("Blend Number created " +
                      str(last_blend_id+1), category='success')

                # update PowderBlendParts records
                last_blend = PowderBlendParts.query.order_by(
                    PowderBlendParts.PartID.desc()).first()
                last_part_id = last_blend.PartID if last_blend else 0
                last_blend_id = int(last_blend.BlendID +
                                    1) if last_blend else 0

                for x in range(len(numbers)):
                    new_blend = PowderBlendParts(
                        PartID=int(last_part_id + 1),
                        BlendID=int(last_blend_id),
                        PartBlendID=int(numbers[x]),
                        PartBatchID=None,
                        AddedWeight=float(weights[x])
                    )
                    db.session.add(new_blend)
                    last_part_id += 1

                for x in range(len(batchs)):
                    new_blend = PowderBlendParts(
                        PartID=int(last_part_id + 1),
                        BlendID=int(last_blend_id),
                        PartBlendID=None,
                        PartBatchID=batchs[x],
                        AddedWeight=float(batchWeights[x])
                    )
                    db.session.add(new_blend)
                    last_part_id += 1

                db.session.commit()
                # Call BlendDatabaseUpdater to update the blend calculations
                updater = BlendDatabaseUpdater(blend_limit=500, frac_limit=0.0001)
                updater.update_blend_database(numbers, weights,db)

                numbers.clear()
                weights.clear()
                batchs.clear()
                batchWeights.clear()
                materials.clear()

            else:
                flash("Selected materials do not match", category='error')

    return render_template("createBlend.html", user=current_user, blends=numbers, blendWeights=weights,
                           batchs=batchs, batchWeights=batchWeights, materials=materials,
                           totalWeight=sum([float(blendWeight) for blendWeight in weights] +
                                           [float(batchWeight) for batchWeight in batchWeights]),
                           type=blendOrBatch)


@views.route('/removeBlend/<int:blendIndex>', methods=['POST'])
@login_required
def remove_blend(blendIndex):
    if blendIndex < len(numbers):
        numbers.pop(blendIndex)
        weights.pop(blendIndex)
        materials.pop(blendIndex)
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
    materials_table = MaterialsTable.query.order_by(
        MaterialsTable.MaterialName, MaterialsTable.SupplierProduct).all()
    products = [material.SupplierProduct for material in materials_table]
    material = {
        material.SupplierProduct: material.MaterialName for material in materials_table}

    if request.method == 'POST':
        poNumber = request.form.get('poNumber', '')
        vlot = request.form.get('vLot', '')
        weight = request.form.get('weight', '')
        product = request.form.get('material', '')

        if not poNumber:
            flash("Missing PO Number. Please Enter a PO Number.", category='error')
        elif not vlot:
            flash("Missing Virgin Lot. Please Enter a Virgin Lot.", category='error')
        elif not weight:
            flash("Missing Weight. Please Enter a Weight.", category='error')
        elif not product:
            flash("Missing material. Please Select a Material.", category='error')
        elif not weight.isnumeric():
            flash("Weight must be a numeric value.", category='error')
        else:
            flash("Batch has been created", category='success')

            product = product.split(" - (")[1]
            product = product.split(' )')[0]
            # Get product id
            product_obj = MaterialsTable.query.filter_by(
                SupplierProduct=product).first()
            if product_obj:
                product_id = product_obj.ProductID

                # Update PowderBlendParts records
                last_batch = InventoryVirginBatch.query.order_by(
                    InventoryVirginBatch.BatchID.desc()).first()
                last_batch_id = last_batch.BatchID if last_batch else 0

                new_batch = InventoryVirginBatch(
                    BatchID=int(last_batch_id + 1),
                    BatchCreatedBy=current_user.id,
                    BatchTimeStamp=str(
                        datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")),
                    BatchFacilityID=int(4),
                    VirginPO=int(poNumber),
                    VirginLot=str(vlot),
                    VirginQty=float(weight),
                    ProductID=int(product_id)
                )
                flash(product_id, category='success')
                # db.session.add(new_batch)
                # db.session.commit()

            else:
                flash("Product not found." + str(product), category='error')
                # Additional error handling code if needed

    return render_template("createBatch.html", user=current_user, Products=products, material_name=material)


@views.route('/BlendHistory', methods=['GET', 'POST'])
@login_required
def blend_history():
    search = None
    query = db.session.query(PowderBlends, MaterialsTable.MaterialName)\
        .join(MaterialsTable, PowderBlends.MaterialID == MaterialsTable.MaterialID)\
        .order_by(PowderBlends.BlendID.desc())

    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            query = query.filter(PowderBlends.BlendID.contains(search))

    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of rows to display per page
    blends = query.paginate(page=page, per_page=per_page)

    return render_template('blend_history.html', user=current_user, blends=blends, search=search)


@views.route('/Report', methods=['GET', 'Post'])
@login_required
def report():

    return render_template('blend_history.html', user=current_user)


