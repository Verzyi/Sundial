from flask import Blueprint, render_template, request, flash, redirect, url_for, session, make_response, Flask, make_response
from jinja2 import Environment, PackageLoader, select_autoescape
from .models import PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from . import db
from flask_login import login_user, login_required, current_user
from datetime import datetime
from sqlalchemy import func, join, and_, create_engine
from sqlalchemy.orm import joinedload
import socket
from datetime import datetime
from .blend_calculator import BlendDatabaseUpdater, PowderBlendCalc
import pandas as pd
import pdfkit
from pdfkit.api import configuration
from collections import defaultdict

# by using configuration you can add path value.
wkhtml_path = pdfkit.configuration(
    wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

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
                            .filter(PowderBlends.BlendID == blendNumber)\
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

        elif 'Trace' in request.form:
            flash("Making Trace", category='success')
            # Retrieve the blend number from session
            blend_number = session.get('last_blend_number')
            if blend_number:
                return redirect(url_for('views.BlendTraceback', blend=blend_number, lvl=0, limit=10))

        elif 'Report' in request.form:
            flash("Making Trace", category='success')
            # Retrieve the blend number from session
            blend_number = session.get('last_blend_number')
            if blend_number:
                return redirect(url_for('views.BlendReport', blend=blend_number))

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


@views.route('/searchBatchs', methods=['GET', 'POST'])
@login_required
def searchBatchs():
    batches = None

    if request.method == 'POST':
        if 'search' in request.form:

            batchNumber = request.form.get('BatchNum')

            if batchNumber:
                query = db.session.query(InventoryVirginBatch, MaterialsTable.MaterialName, MaterialsTable.SupplierProduct) \
                    .join(MaterialsTable, InventoryVirginBatch.ProductID == MaterialsTable.ProductID) \
                    .order_by(InventoryVirginBatch.BatchID.desc()) \
                    .filter(InventoryVirginBatch.BatchID == batchNumber)

                batches = query.all()  # Retrieve the batch search results
                if batches:
                    flash("Found Batch number: " +
                          str(batchNumber), category='success')
                    # Store the blend number in session
                    session['last_batch_number'] = batchNumber
                else:
                    flash("Batch number not found", category='error')

        elif 'Print' in request.form:
            printerName = request.form.get("printer")
            qty = request.form.get("qty")

            if printerName == 'Shop printer':
                printer_ip = '10.101.102.21'
            elif printerName == 'Programmers printer':
                printer_ip = '10.101.102.65'

            batch_number = session.get('last_batch_number')

            if batch_number:
                query = db.session.query(InventoryVirginBatch, MaterialsTable.MaterialName, MaterialsTable.SupplierProduct) \
                    .join(MaterialsTable, InventoryVirginBatch.ProductID == MaterialsTable.ProductID) \
                    .order_by(InventoryVirginBatch.BatchID.desc()) \
                    .filter(InventoryVirginBatch.BatchID == batch_number)

                batches = query.all()  # Retrieve the batch search results

                if batches:
                    for batch, material_name, supplier_product in batches:
                        blend_number = batch.BatchID
                        weight = batch.VirginQty
                        date = batch.BatchTimeStamp
                        material = material_name

                        # Print the sticker
                        print_sticker(printer_ip, blend_number,
                                      material, date, weight, qty)

                    flash("Batch printed: " + str(qty), category='success')
                else:
                    flash("No batch found: " +
                          str(batch_number), category='error')
            else:
                flash("Batch number not found in session", category='error')

    return render_template("searchBatchs.html", user=current_user, batch=batches)


numbers = []
weights = []
batchs = []
batchWeights = []
materials = []


@views.route('/createBlend', methods=['GET', 'POST'])
@login_required
def create_blend():

    blendOrBatch = 'Blend'

    if request.method == 'POST':
        blendNumber = request.form.get('BlendNumber')

        if 'add' in request.form:
            weight = request.form.get('weight')

            if blendNumber is not None and weight is not None and blendNumber != "" and weight != "":
                if float(weight) > 1:
                    radioOption = request.form.get('option')

                    if radioOption == 'Blend':
                        if blendNumber in numbers:
                            flash("Blend number is already added",
                                  category='error')
                        else:
                            search = PowderBlends.query.filter_by(
                                BlendID=blendNumber).first()

                            if search:
                                blendWeight = search.TotalWeight
                                material_id = search.MaterialID
                                query = db.session.query(MaterialsTable.MaterialName).join(
                                    PowderBlends, MaterialsTable.MaterialID == PowderBlends.MaterialID
                                ).filter(PowderBlends.MaterialID == material_id)
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
                        if blendNumber in batchs:
                            flash("Batch number is already added",
                                  category='error')
                        else:
                            search = InventoryVirginBatch.query.filter_by(
                                BatchID=blendNumber).scalar()

                            if search:
                                batchWeight = search.VirginQty

                                if float(batchWeight) < float(weight):
                                    flash("Batch cannot exceed the available weight (" +
                                          str(batchWeight) + " Kg)", category='error')
                                else:
                                    flash("Batch entry added",
                                          category='success')
                                    batchs.append(blendNumber)
                                    batchWeights.append(weight)
                                    material_id = search.ProductID
                                    query = db.session.query(MaterialsTable.MaterialName).join(
                                        InventoryVirginBatch, MaterialsTable.ProductID == InventoryVirginBatch.ProductID
                                    ).filter(InventoryVirginBatch.ProductID == material_id)
                                    material = query.first()[0]
                                    materials.append(material)
                            else:
                                flash("Batch number does not exist",
                                      category='error')

        elif 'create' in request.form:
            if materials == []:
                flash("No items to blend", category='error')
            elif all(x == materials[0] for x in materials):
                material_name = session.get('material_name')
                material = MaterialsTable.query.filter_by(
                    MaterialName=material_name).first()

                if material:
                    material_id = material.ProductID
                    blendWeight = sum(
                        [float(w) for w in weights] + [float(w) for w in batchWeights])

                    if blendWeight > 0:
                        last_blend = PowderBlends.query.order_by(
                            PowderBlends.BlendID.desc()).first()
                        last_blend_id = last_blend.BlendID if last_blend else 0

                        new_blend = PowderBlends(
                            BlendID=last_blend_id + 1,
                            BlendDate=datetime.now().strftime("%m/%d/%Y %H:%M").lstrip("0").replace(" 0", " "),
                            BlendCreatedBy=current_user.id,
                            MaterialID=material_id,
                            TotalWeight=blendWeight
                        )
                        db.session.add(new_blend)
                        db.session.commit()

                        flash("Blend number created: " +
                              str(last_blend_id + 1), category='success')

                        last_part_id = 0
                        if PowderBlendParts.query.count() > 0:
                            last_part_id = db.session.query(
                                func.max(PowderBlendParts.PartID)).scalar()

                        for i, number in enumerate(numbers):
                            new_part = PowderBlendParts(
                                PartID=last_part_id + i + 1,
                                BlendID=last_blend_id + 1,
                                PartBlendID=number,
                                PartBatchID=None,
                                AddedWeight=float(weights[i])
                            )
                            db.session.add(new_part)

                        for i, batch in enumerate(batchs):
                            new_part = PowderBlendParts(
                                PartID=last_part_id + len(numbers) + i + 1,
                                BlendID=last_blend_id + 1,
                                PartBlendID=None,
                                PartBatchID=batch,
                                AddedWeight=float(batchWeights[i])
                            )
                            db.session.add(new_part)

                        db.session.commit()

                        updater = BlendDatabaseUpdater(
                            blend_limit=500, frac_limit=0.0001)
                        updater.update_blend_database(numbers, weights)

                        numbers.clear()
                        weights.clear()
                        batchs.clear()
                        batchWeights.clear()
                        materials.clear()
                        session.pop('material_name', None)
                    else:
                        flash("Blend weight must be greater than 0",
                              category='error')
                else:
                    flash("Selected material does not exist", category='error')
            else:
                flash("Selected materials do not match", category='error')

    return render_template("createBlend.html", user=current_user, blends=numbers, blendWeights=weights,
                           batchs=batchs, batchWeights=batchWeights, materials=materials,
                           totalWeight=sum(
                               [float(w) for w in weights] + [float(w) for w in batchWeights]),
                           type=blendOrBatch)


@views.route('/removeBlend/<int:blendIndex>', methods=['POST'])
@login_required
def remove_blend(blendIndex):
    if blendIndex < len(numbers):
        numbers.pop(blendIndex)
        weights.pop(blendIndex)
        materials.pop(blendIndex)
    if not numbers:  # Check if the numbers list is empty
        session.pop('material_name', None)  # Clear the session variable
    return redirect(url_for('views.create_blend'))


@views.route('/removeBatch/<int:batchIndex>', methods=['POST'])
@login_required
def remove_batch(batchIndex):
    if batchIndex < len(batchs):
        batchs.pop(batchIndex)
        batchWeights.pop(batchIndex)
        materials.pop(batchIndex)
    return redirect(url_for('views.create_blend'))


@views.route('/createBatch', methods=['GET', 'POST'])
@login_required
def create_batch():

    materials_table = MaterialsTable.query.order_by(
        MaterialsTable.SupplierProduct, MaterialsTable.MaterialName).all()

    material_names = [material.MaterialName for material in materials_table]

    material_products = {}
    for material in materials_table:
        if material.MaterialName not in material_products:
            material_products[material.MaterialName] = []
        material_products[material.MaterialName].append(
            material.SupplierProduct)

    if request.method == 'POST':
        poNumber = request.form.get('poNumber', '')
        vlot = request.form.get('vLot', '')
        weight = request.form.get('weight', '')
        material = request.form.get('material', '')
        product = request.form.get('product', '')

        if not poNumber:
            flash("Missing PO Number. Please enter a PO Number.", category='error')
        elif not vlot:
            flash("Missing Virgin Lot. Please enter a Virgin Lot.", category='error')
        elif not weight:
            flash("Missing Weight. Please enter a Weight.", category='error')
        elif not product:
            flash("Missing product. Please select a Product.", category='error')
        elif not weight.isnumeric():
            flash("Weight must be a numeric value.", category='error')
        else:
            flash("Batch has been created", category='success')

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

    return render_template("createBatch.html", user=current_user, material_name=material_names, material_products=material_products)


@views.route('/BlendHistory', methods=['GET', 'POST'])
@login_required
def blend_history():
    material_name = None
    query = db.session.query(PowderBlends, MaterialsTable.MaterialName)\
        .join(MaterialsTable, PowderBlends.MaterialID == MaterialsTable.MaterialID)\
        .order_by(PowderBlends.BlendID.desc())

    if request.method == 'POST':
        material_name = request.form.get('material')

        if material_name:
            query = query.filter(MaterialsTable.MaterialName == material_name)

    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of rows to display per page
    blends = query.paginate(page=page, per_page=per_page)

    material_names = db.session.query(
        MaterialsTable.MaterialName).distinct().all()
    material_names = [name[0] for name in material_names]

    return render_template('blend_history.html', user=current_user, blends=blends, material_name=material_names, selected_material=material_name)


@views.route('/BatchHistory', methods=['GET', 'POST'])
@login_required
def batch_history():
    material_name = None
    query = db.session.query(InventoryVirginBatch, MaterialsTable.MaterialName, MaterialsTable.SupplierProduct)\
        .join(MaterialsTable, InventoryVirginBatch.ProductID == MaterialsTable.ProductID)\
        .order_by(InventoryVirginBatch.BatchID.desc())

    if request.method == 'POST':
        material_name = request.form.get('material')

        if material_name:
            query = query.filter(MaterialsTable.MaterialName == material_name)

    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of rows to display per page
    blends = query.paginate(page=page, per_page=per_page)

    material_names = db.session.query(
        MaterialsTable.MaterialName).distinct().all()
    material_names = [name[0] for name in material_names]

    supplier_product = db.session.query(
        MaterialsTable.SupplierProduct).distinct().all()
    supplier_product = [name[0] for name in supplier_product]

    return render_template('Batch_history.html', user=current_user, batchs=blends, material_name=material_names, supplier_name=supplier_product, selected_material=material_name)


@views.route('/BlendReport', methods=['GET', 'Post'])
@login_required
def BlendReport():
    blend = request.args.get('blend')
    blend = int(blend)

    # import `powder_blend_calc`
    calcTable = "Powder_Blend_Calc"
    powder_blend_calc = pd.read_sql(
        f"SELECT * FROM {calcTable}", con=db.engine)
    powder_blend_calc[['BlendID', 'PartID']] = powder_blend_calc[[
        'BlendID', 'PartID']].astype('Int64')
    # import `inventory_virgin_batch`
    batchTable = "Inventory_Virgin_Batch"
    inventory_virgin_batch = pd.read_sql(
        f"SELECT * FROM {batchTable}", con=db.engine)
    inventory_virgin_batch[['BatchID', 'ProductID']] = inventory_virgin_batch[['BatchID', 'ProductID']] \
        .astype('Int64')
    # import `powder_material`
    materialTable = "materials_table"
    powder_material = pd.read_sql(
        f"SELECT * FROM {materialTable}", con=db.engine)
    powder_material[['MaterialID', 'ProductID']] = powder_material[[
        'MaterialID', 'ProductID']].astype('Int64')
    # import `powder_blend`
    blendsTable = "powder_blends"
    powder_blend = pd.read_sql(f"SELECT * FROM {blendsTable}", con=db.engine)
    powder_blend[['MaterialID', 'BlendID']] = powder_blend[[
        'MaterialID', 'BlendID']].astype('Int64')
    # import `powder_blend_part`
    blendPartTable = "Powder_Blend_Parts"
    powder_blend_part = pd.read_sql(
        f"SELECT * FROM {blendPartTable}", con=db.engine)
    powder_blend_part[['BlendID', 'PartID', 'PartBlendID', 'PartBatchID']] \
        = powder_blend_part[['BlendID', 'PartID', 'PartBlendID', 'PartBatchID']].astype('Int64')

    # create new DF for requested Blend
    blend_data = powder_blend_calc[powder_blend_calc['BlendID'] == blend].copy(
    )
    blend_data = blend_data.merge(powder_blend_part[['PartID', 'PartBatchID']],
                                  on=['PartID'], how='left', validate='m:1')
    # blend_data = blend_data.merge(inventory_virgin_batch[['BatchID', 'VirginPO', 'VirginLot', 'ProductID']], \
    #         left_on=['PartBatchID'], right_on=['BatchID'], how='left', validate='m:1')
    blend_data.rename(columns={'PartBatchID': 'BatchID'}, inplace=True)
    blend_data = blend_data.merge(inventory_virgin_batch[['BatchID', 'VirginPO', 'VirginLot', 'ProductID']],
                                  on=['BatchID'], how='left', validate='m:1')
    blend_data.sort_values(by=['PartFraction'], ascending=False, inplace=True)

    product_dict = powder_material[['ProductID', 'SupplierProduct']].drop_duplicates(keep='first') \
        .set_index('ProductID')['SupplierProduct'].to_dict()
    blend_data['SupplierProduct'] = blend_data['ProductID'].map(product_dict)

    material_id = powder_blend.set_index(
        'BlendID')['MaterialID'].to_dict()[blend]
    material = powder_material.set_index(
        'MaterialID')['MaterialName'].to_dict()[material_id]
    # material = material_id.map(mat_dict)
    total_weight = powder_blend[powder_blend['BlendID']
                                == blend]['TotalWeight'].iloc[0]
    count_avg = round((blend_data['PartFraction']
                      * blend_data['SieveCount']).sum())
    count_max = blend_data['SieveCount'].max()

    summary_dict = {'Blend': blend,
                    'Material': material,
                    'Total Weight (kg)': total_weight,
                    'Avg. Sieve Count': count_avg,
                    'Max. Sieve Count': count_max,
                    }
    blend_summary = pd.DataFrame(summary_dict, index=['Value']).T
    blend_summary.fillna(value='---', inplace=True)
    # blend_summary.reset_index(names='Summary', inplace=True)

    # Create new DF for data grouped by Batch
    grouped = blend_data.groupby(by=['BatchID'], as_index=False).sum(
        numeric_only=True)[['BatchID', 'PartFraction']].copy()
    grouped.sort_values(by=['PartFraction'], ascending=False, inplace=True)
    grouped = grouped.merge(inventory_virgin_batch[['BatchID', 'VirginPO', 'VirginLot', 'ProductID',]],
                            on=['BatchID'], how='left', validate='m:1')
    grouped['SupplierProduct'] = grouped['ProductID'].map(product_dict)
    maj = grouped.iloc[0]
    maj_batch = maj['BatchID'].astype(str).replace('.0', '')
    maj_prod = maj['SupplierProduct']
    maj_po = maj['VirginPO']
    maj_lot = maj['VirginLot']
    maj_per = maj['PartFraction'] * 100
    maj_per = f'{maj_per:.1f}%'

    majority_dict = {'BatchID': maj_batch,
                     'Percentage': maj_per,
                     'Supplier Product': maj_prod,
                     'Purchase Order': maj_po,
                     'Virgin Lot': maj_lot,
                     }
    majority_batch = pd.DataFrame(majority_dict, index=['Value']).T
    # majority_batch.loc['BatchID', 'Value'] = int(majority_batch.loc['BatchID', 'Value'])
    majority_batch.fillna(value='---', inplace=True)

    # Create a DF of the top 20 blend constituents
    top = 30
    blend_breakdown = blend_data.head(top).copy()
    blend_breakdown['Percent'] = blend_breakdown['PartFraction'] * 100
    blend_breakdown = blend_breakdown[['BatchID', 'SupplierProduct', 'VirginPO', 'VirginLot', 'Percent',
                                       'SieveCount']]
    blend_breakdown.rename(columns={'SupplierProduct': 'Product',
                                    'VirginPO': 'Purchase Order',
                                    'VirginLot': 'Virgin Lot',
                                    'SieveCount': 'Sieve Count',
                                    }, inplace=True)
    other_per = 100.000001 - blend_breakdown['Percent'].sum()
    # decimal.getcontext().rounding = decimal.ROUND_CEILING
    # other_per = float(round(decimal.Decimal(str(other_per)), ndigits=3))
    blend_breakdown[['BatchID']] = blend_breakdown[['BatchID']].astype(str)
    blend_breakdown.reset_index(drop=True, inplace=True)
    blend_breakdown.loc[blend_breakdown.shape[0]] = [
        '', '', 'Other', '', other_per, '']
    blend_breakdown['Percent'] = blend_breakdown['Percent'].map(
        '{:.1f}%'.format)
    blend_breakdown.fillna(value='---', inplace=True)

    print("Blend Summary:")
    print(blend_summary)
    print("\nMajority Batch:")
    print(majority_batch)
    print("\nBlend Breakdown:")
    print(blend_breakdown)

    rendered = render_template('Blend_Report.html',
                               blend_summary=blend_summary,
                               majority_batch=majority_batch,
                               blend_breakdown=blend_breakdown)
    pdf = pdfkit.from_string(rendered, False, configuration=wkhtml_path)

    response = make_response(pdf)
    response.headers['Content-type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={blend}_Report.pdf'
    return response


@views.route('/TraceBack/<int:blend>/<int:lvl>/<int:limit>', methods=['GET', 'POST'])
@login_required
def BlendTraceback(blend, lvl, limit):
    blendPartTable = "Powder_Blend_Parts"
    powder_blend_part = pd.read_sql(
        f"SELECT * FROM {blendPartTable}", con=db.engine)
    blendsTable = "powder_blends"
    powder_blend = pd.read_sql(f"SELECT * FROM {blendsTable}", con=db.engine)

    powder_blend_part[['PartBlendID', 'PartBatchID']] = powder_blend_part[[
        'PartBlendID', 'PartBatchID']].astype('Int64')

    blend_df = powder_blend_part[powder_blend_part['BlendID'] == blend].copy()
    blend_df['TotalWeight'] = blend_df['BlendID'].map(
        powder_blend.set_index('BlendID')['TotalWeight'])
    blend_df['PartFraction'] = blend_df['AddedWeight'] / \
        blend_df['TotalWeight']

    tracebacks = []  # List to store the tracebacks

    if lvl == 0:
        total_weight = blend_df['TotalWeight'].max()
        blend_date = powder_blend.loc[powder_blend['BlendID']
                                      == blend, 'BlendDate'].values[0]
        tracebacks.append(
            f'{lvl}: Blend {blend} ({total_weight:.2f} kg) (Date: {blend_date})')

    if limit > 0:
        for i, r in blend_df.iterrows():
            old_blend = r['PartBlendID']
            batch = r['PartBatchID']
            frac = r['PartFraction']
            new_lvl = lvl + 1

            if old_blend is not pd.NA:
                blend_weight = powder_blend.loc[powder_blend['BlendID']
                                                == old_blend, 'TotalWeight'].values[0]
                blend_date = powder_blend.loc[powder_blend['BlendID']
                                              == old_blend, 'BlendDate'].values[0]
                tracebacks.append(
                    f'{new_lvl}: {"..." * new_lvl} Blend {old_blend} ({frac * 100:.0f}%) (Weight: {blend_weight:.2f} kg) (Date: {blend_date})')
                new_limit = limit - 1
                tracebacks.extend(BlendTraceback(
                    old_blend, new_lvl, new_limit))

            elif old_blend is pd.NA:
                batch_weight = powder_blend_part.loc[powder_blend_part['PartBatchID'] == batch, 'AddedWeight'].sum(
                )
                batch_date = powder_blend.loc[powder_blend['BlendID']
                                              == blend, 'BlendDate'].values[0]
                tracebacks.append(
                    f'{new_lvl}: {"..." * new_lvl} Batch {batch} ({frac * 100:.0f}%) (Weight: {batch_weight:.2f} kg) (Date: {batch_date})')

    cleaned_tracebacks = [traceback.strip(
    ) for traceback in tracebacks if traceback.strip()]  # Remove unwanted characters
    return cleaned_tracebacks


@views.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    # Retrieve the blend inventory data
    # Retrieve the blend inventory data
    query = db.session.query(
        PowderBlends.BlendID,
        MaterialsTable.MaterialName,
        PowderBlends.CurrentWeight
    ).join(
        MaterialsTable, PowderBlends.MaterialID == MaterialsTable.MaterialID
    )

    # Fetch the blend inventory data
    inventory_data = query.all()

    # Create a DataFrame from the inventory data
    df = pd.DataFrame(inventory_data, columns=[
                      "Blend ID", "Material", "Current Weight"])

    # Filter out blends with weight less than or equal to 20
    df = df[df["Current Weight"] > 20]

    # Calculate subtotal for each material
    df_subtotal = df.groupby("Material").agg({"Current Weight": "sum"})
    df_subtotal = df_subtotal.reset_index()
    df_subtotal["Blend ID"] = "Subtotal"

    # Concatenate the subtotal rows with the blend items
    df_result = pd.concat([df_subtotal, df])

    # Calculate total weight
    total_weight = df_result[df_result["Blend ID"]
                             != "Subtotal"]["Current Weight"].sum()

    # Retrieve the distinct material names
    material_names = df_result["Material"].unique()

    return render_template(
        "inventory.html",
        user=current_user,
        inventory_data=df_result.to_dict(orient="records"),
        material_names=material_names,
        total_weight=total_weight
    )
