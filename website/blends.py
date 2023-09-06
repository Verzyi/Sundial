from flask import Blueprint, render_template, request, flash, redirect, url_for, session, make_response, Flask, make_response
from jinja2 import Environment, PackageLoader, select_autoescape
from flask_login import login_user, login_required, current_user
import datetime as dt
from sqlalchemy import func, join, and_, create_engine
from sqlalchemy.orm import joinedload, aliased
import socket
import pandas as pd
import pdfkit
from pdfkit.api import configuration

from . import db
from .models import PowderBlends, MaterialProducts, MaterialAlloys, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable
from .blend_calculator import BlendDatabaseUpdater, PowderBlendCalc

# by using configuration you can add path value.
wkhtml_path = pdfkit.configuration(
    wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

blends = Blueprint('blends', __name__)


@blends.route('/')
@login_required
def home():
    blends = PowderBlends.query.all()
    return render_template('home.html', user=current_user, blends=blends)


@blends.route('/blend', methods=['GET', 'POST'])
@login_required
def blend():
    return render_template('blend.html', user=current_user)

def PrintSticker(printer_ip, batch_or_blend, batch_blend_id, material, date, weight, qty):
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
        f"^FD{batch_or_blend} ID: {batch_blend_id}^FS",
        f"^FO40,120",  # Adjusted X and Y values for Material text
        f"^A0N,26,19",  # Increased font size for Material text
        f"^FDMaterial: {material}^FS",
        f"^FO40,150",  # Adjusted X and Y values for Weight text
        f"^A0N,26,19",  # Increased font size for Weight text
        f"^FDWeight: {weight} kg^FS",
        f"^FO40,180",  # Adjusted X and Y values for Date text
        f"^A0N,26,19",  # Increased font size for Date text
        f"^FDDate: {date}^FS",
        # Adjusted X and Y values for barcode (moved 0.8" to the left)
        f"^FO260,90",
        f"^BY1.25,2.5,60",  # Adjusted barcode width, height, and darkness
        f"^B3N,N,100,Y,N",
        f"^FD{batch_blend_id}^FS",
        # Copying elements starting at 2.1" from the left edge
        f"^FO460,90",
        f"^A0N,26,19",
        f"^FD{batch_or_blend} ID: {batch_blend_id}^FS",
        f"^FO460,120",
        f"^A0N,26,19",
        f"^FDMaterial: {material}^FS",
        f"^FO460,150",
        f"^A0N,26,19",
        f"^FDWeight: {weight} kg^FS",
        f"^FO460,180",
        f"^A0N,26,19",
        f"^FDDate: {date}^FS",
        f"^FO680,90",
        f"^BY1.25,2.5,60",
        f"^B3N,N,100,Y,N",
        f"^FD{batch_blend_id}^FS",
        f"^PQ{qty}",
        "^XZ"
    ]

    command_string = '\n'.join(commands)
    sock.sendall(command_string.encode())
    # Close the socket
    sock.close()

@blends.route('/search-blend', methods=['GET', 'POST'])
@login_required
def SearchBlends():
    blend_query = None
    batch_or_blend = 'Blend'
    if request.method == 'POST':
        if 'search' in request.form:
            if request.form.get('blend_id') is not None:
                if len(request.form.get('blend_id')) != 0:
                    blend_id = request.form.get('blend_id')
                    # Store the blend number in session
                    session['last_blend_number'] = blend_id

                    if int(request.form.get('blend_id')) > 1:
                        # blend_query = PowderBlends.query.filter_by(BlendID=blend_id).all()

                        blend_query = db.session.query(PowderBlends, MaterialAlloys.AlloyName) \
                            .join(MaterialAlloys, PowderBlends.AlloyID == MaterialAlloys.AlloyID) \
                            .filter(PowderBlends.BlendID == blend_id)\
                            .all()
                        
                        if blend_query:
                            flash(f'Blend {blend_id} found.', category='success')
                        else:
                            flash(f'Blend {blend_id} not found.', category='error')
                    else:
                        flash(f'Blend number must be positive: {blend_id}', category='error')

        elif 'Trace' in request.form:
            flash('Making Trace', category='success')
            # Retrieve the blend number from session
            blend_id = session.get('last_blend_number')
            if blend_id:
                return redirect(url_for('blends.BlendTrace', blend=blend_id, lvl=0, limit=10))

        elif 'Report' in request.form:
            flash('Making Report', category='success')
            # Retrieve the blend number from session
            blend_id = session.get('last_blend_number')
            if blend_id:
                return redirect(url_for('blends.BlendReport', blend=blend_id))

        elif 'Print' in request.form:
            printer_name = request.form.get('printer')
            if printer_name == 'Shop Floor Printer':
                printer_ip = '10.101.102.21'
            elif printer_name == 'Office Printer':
                printer_ip = '10.101.102.65'

                # Retrieve the blend number from session
                blend_id = session.get('last_blend_number')

                if blend_id:
                    blend_query = db.session.query(PowderBlends, MaterialAlloys.AlloyName) \
                        .join(MaterialAlloys, PowderBlends.AlloyID == MaterialAlloys.AlloyID) \
                        .filter(PowderBlends.BlendID == blend_id) \
                        .all()

                    if blend_query:
                        for blend, alloy_name in blend_query:
                            weight = blend.TotalWeight
                            date = blend.BlendDate.split(' ')[0]
                            qty = request.form.get('qty')
                            # Print the sticker
                            PrintSticker(printer_ip, batch_or_blend, blend_id, alloy_name, date, weight, qty)
                        flash(f'Blend {blend_id} sticker(s) printed: qty {qty}', category='success')
                    else:
                        flash(f'Blend {blend_id} not found.', category='error')
                else:
                    flash(f'Blend not found in session.', category='error')
            else:
                flash(f'Error: Blend sticker not printed.', category='error')

    return render_template('search-blend.html', user=current_user, blends=blend_query)


@blends.route('/search-batch', methods=['GET', 'POST'])
@login_required
def SearchBatch():
    batch_query = None
    batch_or_blend = 'Batch'
    if request.method == 'POST':
        if 'search' in request.form:

            batch_id = request.form.get('batch_id')

            if batch_id:
                batch_query = db.session.query(InventoryVirginBatch, MaterialAlloys.AlloyName, MaterialProducts.SupplierProduct) \
                    .join(MaterialProducts, InventoryVirginBatch.ProductID == MaterialProducts.ProductID) \
                        .join(MaterialAlloys, MaterialProducts.AlloyID == MaterialAlloys.AlloyID) \
                    .order_by(InventoryVirginBatch.BatchID.desc()) \
                    .filter(InventoryVirginBatch.BatchID == batch_id).all()
                
                if batch_query:
                    flash(f'Batch {batch_id} found.', category='success')
                    # Store the blend number in session
                    session['last_batch_id'] = batch_id
                else:
                    flash(f'Batch {batch_id} not found.', category='error')

        elif 'Print' in request.form:
            printer_name = request.form.get('printer')
            qty = request.form.get('qty')

            if printer_name == 'Shop Floor Printer':
                printer_ip = '10.101.102.21'
            elif printer_name == 'Office Printer':
                printer_ip = '10.101.102.65'

            batch_id = session.get('last_batch_id')

            if batch_id:
                batch_query = db.session.query(InventoryVirginBatch, MaterialAlloys.AlloyName, MaterialProducts.SupplierProduct) \
                    .join(MaterialProducts, InventoryVirginBatch.ProductID == MaterialProducts.ProductID) \
                        .join(MaterialAlloys, MaterialProducts.AlloyID == MaterialAlloys.AlloyID) \
                    .order_by(InventoryVirginBatch.BatchID.desc()) \
                    .filter(InventoryVirginBatch.BatchID == batch_id).all()

                if batch_query:
                    for batch, alloy_name, supplier_product in batch_query:
                        batch_id = batch.BatchID
                        weight = batch.VirginWeight
                        date = batch.BatchTimeStamp.split(' ')[0]

                        # Print the sticker
                        PrintSticker(printer_ip, batch_or_blend, batch_id, alloy_name, date, weight, qty)

                    flash(f'Batch {batch_id} sticker(s) printed: qty {qty}', category='success')
                else:
                    flash(f'Batch {batch_id} not found.', category='error')
            else:
                flash('Batch number not found in session', category='error')

    return render_template('search-batch.html', user=current_user, batch=batch_query)


numbers = []
weights = []
batch_list = [] 
batchWeights = []
alloy_list = []


@blends.route('/create-blend', methods=['GET', 'POST'])
@login_required
def CreateBlend():
    # blend_or_batch = 'Blend
    if request.method == 'POST':
        batch_blend_id = request.form.get('batch_blend_id')
        if 'add' in request.form:
            weight = request.form.get('weight')
            if batch_blend_id is not None and weight is not None and batch_blend_id != "" and weight != "":
                if float(weight) > 1:
                    radioOption = request.form.get('option')
                    if radioOption == 'Blend':
                        if batch_blend_id in numbers:
                            flash(f'Blend {batch_blend_id} has already been added.',
                                  category='error')
                        else:
                            blend_query = PowderBlends.query.filter_by(BlendID=batch_blend_id).first()

                            if blend_query:
                                blendWeight = blend_query.CurrentWeight
                                alloy_id = blend_query.AlloyID
                                query = db.session.query(MaterialAlloys.AlloyName) \
                                    .join(PowderBlends, MaterialAlloys.AlloyID == PowderBlends.AlloyID) \
                                        .filter(PowderBlends.AlloyID == alloy_id)
                                alloy = query.first()[0]

                                if float(blendWeight) < float(weight):
                                    flash(f'Blend cannot exceed the available weight ({blendWeight} kg)', category='error')
                                else:
                                    flash(f'Blend {batch_blend_id} added',category='success')
                                    numbers.append(batch_blend_id)
                                    weights.append(weight)
                                    alloy_list.append(alloy)
                                    session['alloy_name'] = alloy
                            else:
                                flash(f'Blend {batch_blend_id} does not exist.', category='error')

                    elif radioOption == 'Batch':
                        if batch_blend_id in batch_list:
                            flash(f'Batch {batch_blend_id} has already been added.',
                                  category='error')
                        else:
                            batch_query = InventoryVirginBatch.query.filter_by(
                                BatchID=batch_blend_id).scalar()

                            if batch_query:
                                batchWeight = batch_query.CurrentWeight

                                if float(batchWeight) < float(weight):
                                    flash(f'Batch cannot exceed the available weight ({batchWeight} kg)', category='error')
                                else:
                                    flash(f'Batch {batch_blend_id} added.',
                                          category='success')
                                    batch_list.append(batch_blend_id)
                                    batchWeights.append(weight)
                                    product_id = batch_query.ProductID
                                    query = db.session.query(InventoryVirginBatch, MaterialAlloys.AlloyName) \
                                        .join(MaterialProducts, InventoryVirginBatch.ProductID == MaterialProducts.ProductID) \
                                            .join(MaterialAlloys, MaterialProducts.AlloyID == MaterialAlloys.AlloyID) \
                                                .filter(InventoryVirginBatch.ProductID == product_id)
                                    alloy = query.first()[1]
                                    alloy_list.append(alloy)
                            else:
                                flash('Batch {batch_blend_id} does not exist.', category='error')
                else: flash('Blend weight must be greater than 0 kg.', category='error')
        elif 'create' in request.form:
            if alloy_list == []:
                flash('No items to blend', category='error')
            elif all(x == alloy_list[0] for x in alloy_list):
                alloy_name = session.get('alloy_name')
                alloy = MaterialAlloys.query.filter_by(AlloyName=alloy_name).first()

                if alloy:
                    alloy_id = alloy.AlloyID
                    blendWeight = sum(
                        [float(w) for w in weights] + [float(w) for w in batchWeights])

                    if blendWeight > 0:
                        last_blend = PowderBlends.query.order_by(
                            PowderBlends.BlendID.desc()).first()
                        last_blend_id = last_blend.BlendID if last_blend else 0
                        new_blend_id = last_blend_id + 1

                        new_blend = PowderBlends(
                            BlendID=new_blend_id,
                            BlendDate=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),#.lstrip('0').replace(' 0', ' '),
                            BlendCreatedBy=current_user.id,
                            AlloyID=alloy_id,
                            TotalWeight=blendWeight
                        )
                        db.session.add(new_blend)
                        db.session.commit()

                        flash(f'{alloy_name} Blend {new_blend_id} created!', category='success')

                        last_part_id = 0
                        if PowderBlendParts.query.count() > 0:
                            last_part_id = db.session.query(
                                func.max(PowderBlendParts.PartID)).scalar()

                        for i, number in enumerate(numbers):
                            new_part = PowderBlendParts(
                                PartID=last_part_id + i + 1,
                                BlendID=new_blend_id,
                                PartBlendID=number,
                                PartBatchID=None,
                                AddedWeight=float(weights[i])
                            )
                            db.session.add(new_part)

                        for i, batch in enumerate(batch_list):
                            new_part = PowderBlendParts(
                                PartID=last_part_id + len(numbers) + i + 1,
                                BlendID=new_blend_id,
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
                        batch_list.clear()
                        batchWeights.clear()
                        alloy_list.clear()
                        session.pop('alloy_name', None)
                    else:
                        flash('Blend weight must be greater than 0 kg.', category='error')
                else:
                    flash('Selected material does not exist.', category='error')
            else:
                flash('Selected materials do not match.', category='error')
    totalWeight = sum([float(w) for w in weights] + [float(w) for w in batchWeights])
    return render_template('create-blend.html', user=current_user, blends=numbers, blendWeights=weights,
                           batch_list=batch_list, batchWeights=batchWeights, alloy_list=alloy_list,
                           totalWeight=totalWeight,
                        #    blend_or_batch=blend_or_batch,
                           )


@blends.route('/removeBlend/<int:blendIndex>', methods=['POST'])
@login_required
def RemoveBlend(blendIndex):
    if blendIndex < len(numbers):
        numbers.pop(blendIndex)
        weights.pop(blendIndex)
        alloy_list.pop(blendIndex)
    if not numbers:  # Check if the numbers list is empty
        session.pop('alloy_name', None)  # Clear the session variable
    return redirect(url_for('blends.CreateBlend'))


@blends.route('/removeBatch/<int:batchIndex>', methods=['POST'])
@login_required
def RemoveBatch(batchIndex):
    if batchIndex < len(batch_list):
        batch_list.pop(batchIndex)
        batchWeights.pop(batchIndex)
        alloy_list.pop(batchIndex)
    return redirect(url_for('blends.CreateBlend'))


@blends.route('/create-batch', methods=['GET', 'POST'])
@login_required
def CreateBatch():
    products_table = db.session.query(MaterialProducts.SupplierProduct, MaterialAlloys.AlloyName) \
        .join(MaterialAlloys, MaterialProducts.AlloyID == MaterialAlloys.AlloyID).all()
    # print(products_table)
    alloy_names = sorted(set([product.AlloyName for product in products_table]))
    # print(alloy_names)
    material_products = {}
    for product in products_table:
        if product.AlloyName not in material_products:
            material_products[product.AlloyName] = []
        material_products[product.AlloyName].append(
            product.SupplierProduct)
    # print(material_products)
    if request.method == 'POST':
        poNumber = request.form.get('poNumber', '')
        vlot = request.form.get('vLot', '')
        weight = request.form.get('weight', '')
        product = request.form.get('product', '')

        if not poNumber:
            flash('Missing PO Number. Please enter a PO Number.', category='error')
        elif not vlot:
            flash('Missing Virgin Lot. Please enter a Virgin Lot.', category='error')
        elif not weight:
            flash('Missing Weight. Please enter a Weight.', category='error')
        elif not product:
            flash('Missing product. Please select a Product.', category='error')
        elif not weight.isnumeric():
            flash('Weight must be a numeric value.', category='error')
        else:
            # Get product id
            product_obj = MaterialProducts.query.filter_by(
                SupplierProduct=product).first()
            if product_obj:
                product_id = product_obj.ProductID

                # Update InventoryVirginBatch records
                last_batch = InventoryVirginBatch.query.order_by(
                    InventoryVirginBatch.BatchID.desc()).first()
                last_batch_id = last_batch.BatchID if last_batch else 0
                new_batch_id = int(last_batch_id + 1)

                new_batch = InventoryVirginBatch(
                    BatchID=new_batch_id,
                    BatchCreatedBy=current_user.id,
                    BatchTimeStamp=str(
                    dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    BatchFacilityID=int(4),
                    VirginPO=int(poNumber),
                    VirginLot=str(vlot),
                    VirginWeight=float(weight),
                    ProductID=int(product_id)
                )
                # flash(product_id, category='success')
                db.session.add(new_batch)
                db.session.commit()
                
                flash(f'Batch {new_batch_id} has been created', category='success')
            else:
                flash(f'Product {product} not found.', category='error')
                # Additional error handling code if needed

    return render_template('create-batch.html', user=current_user, alloy_names=alloy_names, \
        material_products=material_products)


@blends.route('/history-blend', methods=['GET', 'POST'])
@login_required
def HistoryBlend():
    alloy_name = None
    query = db.session.query(PowderBlends, MaterialAlloys.AlloyName)\
        .join(MaterialAlloys, PowderBlends.AlloyID == MaterialAlloys.AlloyID)\
        .order_by(PowderBlends.BlendID.desc())

    if request.method == 'POST':
        alloy_name = request.form.get('alloy')
        if alloy_name:
            query = query.filter(MaterialAlloys.AlloyName == alloy_name)

    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of rows to display per page
    blends = query.paginate(page=page, per_page=per_page)

    alloy_names = db.session.query(MaterialAlloys.AlloyName).distinct().all()
    alloy_names = [name[0] for name in alloy_names]

    return render_template('history-blend.html', user=current_user, blends=blends, alloy_names=alloy_names, \
        selected_alloy=alloy_name)


@blends.route('/history-batch', methods=['GET', 'POST'])
@login_required
def HistoryBatch():
    alloy_name = None
    batch_query = db.session.query(InventoryVirginBatch, MaterialAlloys.AlloyName, MaterialProducts.SupplierProduct)\
        .join(MaterialProducts, InventoryVirginBatch.ProductID == MaterialProducts.ProductID) \
            .join(MaterialAlloys, MaterialProducts.AlloyID == MaterialAlloys.AlloyID) \
                .order_by(InventoryVirginBatch.BatchID.desc())

    if request.method == 'POST':
        alloy_name = request.form.get('alloy')

        if alloy_name:
            batch_query = batch_query.filter(MaterialAlloys.AlloyName == alloy_name)

    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of rows to display per page
    blends = batch_query.paginate(page=page, per_page=per_page)

    alloy_names = db.session.query(
        MaterialAlloys.AlloyName).distinct().all()
    alloy_names = [name[0] for name in alloy_names]

    supplier_product = db.session.query(
        MaterialProducts.SupplierProduct).distinct().all()
    supplier_product = [name[0] for name in supplier_product]

    return render_template('history-batch.html', user=current_user, batch_list=blends, alloy_names=alloy_names, supplier_name=supplier_product, selected_alloy=alloy_name)


@blends.route('/blend-report', methods=['GET', 'Post'])
@login_required
def BlendReport():
    blend = request.args.get('blend')
    blend = int(blend)

    # import `powder_blend_calc`
    calcTable = 'powder_blend_calc'
    powder_blend_calc = pd.read_sql(
        f"SELECT * FROM {calcTable}", con=db.engine)
    powder_blend_calc[['BlendID', 'PartID']] = powder_blend_calc[[
        'BlendID', 'PartID']].astype('Int64')
    # import `inventory_virgin_batch`
    batchTable = "inventory_virgin_batch"
    inventory_virgin_batch = pd.read_sql(
        f"SELECT * FROM {batchTable}", con=db.engine)
    inventory_virgin_batch[['BatchID', 'ProductID']] = inventory_virgin_batch[['BatchID', 'ProductID']] \
        .astype('Int64')
    # import `material_alloys`
    alloysTable = "material_alloys"
    material_alloys = pd.read_sql(
        f"SELECT * FROM {alloysTable}", con=db.engine)
    material_alloys[['AlloyID']] = material_alloys[[
        'AlloyID']].astype('Int64')
    # import `material_alloys`
    productsTable = "material_products"
    material_products = pd.read_sql(
        f"SELECT * FROM {productsTable}", con=db.engine)
    material_products[['ProductID']] = material_products[[
        'ProductID']].astype('Int64')
    # import `powder_blend`
    blendsTable = "powder_blends"
    powder_blend = pd.read_sql(f"SELECT * FROM {blendsTable}", con=db.engine)
    powder_blend[['AlloyID', 'BlendID']] = powder_blend[[
        'AlloyID', 'BlendID']].astype('Int64')
    # import `powder_blend_part`
    blendPartTable = "powder_blend_parts"
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

    product_dict = material_products[['ProductID', 'SupplierProduct']].drop_duplicates(keep='first') \
        .set_index('ProductID')['SupplierProduct'].to_dict()
    blend_data['SupplierProduct'] = blend_data['ProductID'].map(product_dict)

    alloy_id = powder_blend.set_index('BlendID')['AlloyID'].to_dict()[blend]
    alloy_name = material_alloys.set_index('AlloyID')['AlloyName'].to_dict()[alloy_id]
    # material = alloy_id.map(mat_dict)
    total_weight = powder_blend[powder_blend['BlendID']
                                == blend]['TotalWeight'].iloc[0]
    count_avg = round((blend_data['PartFraction']
                      * blend_data['SieveCount']).sum())
    count_max = blend_data['SieveCount'].max()

    summary_dict = {'Blend': blend,
                    'Material': alloy_name,
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
    
    footer = f'Report generated on: {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

    # print('Blend Summary:')
    # print(blend_summary)
    # print('\nMajority Batch:')
    # print(majority_batch)
    # print('\nBlend Breakdown:')
    # print(blend_breakdown)
    # print('\nReport Generated:')
    # print(footer_html)

    rendered = render_template('blend-report.html',
                               blend_summary=blend_summary,
                               majority_batch=majority_batch,
                               blend_breakdown=blend_breakdown,
                               footer=footer)
    pdf = pdfkit.from_string(rendered, False, configuration=wkhtml_path)

    response = make_response(pdf)
    response.headers['Content-type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={blend}_Report.pdf'
    return response


@blends.route('/trace/<int:blend>/<int:lvl>/<int:limit>', methods=['GET', 'POST'])
@login_required
def BlendTrace(blend, lvl, limit):
    blendPartTable = 'powder_blend_parts'
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
                tracebacks.extend(BlendTrace(old_blend, new_lvl, new_limit))

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


@blends.route('/BlendInventory', methods=['GET', 'POST'])
@login_required
def Blend_Inventory():
    # Import necessary libraries
    import datetime
    from sqlalchemy import func
    from sqlalchemy.orm import aliased

    # Define aliases for the tables
    PowderBlendsAlias = aliased(PowderBlends)
    MaterialAlloysAlias = aliased(MaterialAlloys)

    # Retrieve the blend inventory data
    inventory_query = db.session.query(
        PowderBlendsAlias.BlendID,
        MaterialAlloysAlias.AlloyName,
        PowderBlendsAlias.CurrentWeight,
        PowderBlendsAlias.BlendDate
    ).join(
        MaterialAlloysAlias, PowderBlendsAlias.AlloyID == MaterialAlloysAlias.AlloyID
    ).order_by(MaterialAlloysAlias.AlloyName).all()

    # Fetch the blend inventory data
    inventory_query = inventory_query.all()

    # Create a list to store the result data
    result_data = []

    # Variables for subtotal calculation
    current_alloy = None
    subtotal_weight = 0

    # Set to store blend IDs
    blend_ids_set = set()

    # Iterate over the inventory data
    for blend_id, alloy_name, total_weight, blend_date in inventory_query:
        # Check if the material has changed
        if alloy_name != current_alloy:
            # Add subtotal row for previous material
            if current_alloy is not None:
                subtotal_row = ('Subtotal', current_alloy, subtotal_weight)
                result_data.append(subtotal_row)

            # Update current material and reset subtotal weight
            current_alloy = alloy_name
            subtotal_weight = 0

        # Check if blend_date is not None before converting to datetime.date object
        if blend_date is not None:
            blend_date = dt.datetime.strptime(blend_date, '%Y-%m-%d %H:%M:%S').date()

        # Add blend row if BlendDate is after 8/1/2022 and current weight > 20 and blend ID not in set
        if (
            blend_date is not None
            and blend_date > dt.date(2021, 8, 1)
            and total_weight is not None
            and total_weight > 20
            and blend_id not in blend_ids_set
        ):
            blend_row = (blend_id, alloy_name, total_weight)
            result_data.append(blend_row)

            # Update subtotal weight
            if total_weight is not None:
                subtotal_weight += total_weight

            # Add blend ID to set
            blend_ids_set.add(blend_id)

    # Add final subtotal row for the last material
    if current_alloy is not None:
        subtotal_row = ('Subtotal', current_alloy, round(subtotal_weight, 2))
        result_data.append(subtotal_row)


    # Calculate total weight
    total_weight = sum(row[2] for row in result_data if isinstance(row[2], (int, float)))

    # Get distinct material names
    alloy_names = sorted(set(row[1] for row in result_data))
    

    # Filter by selected material name
    selected_alloy = request.form.get('alloy') # or request.args.get('material')
    if selected_alloy and selected_alloy != 'All Materials':
        filtered_data = [row for row in result_data if row[1] == selected_alloy]
    else:
        filtered_data = result_data

    return render_template(
        "blend_inventory.html",
        user=current_user,
        inventory_data=filtered_data,
        material_names=material_names,
        total_weight=total_weight,
        selected_material=selected_material
    )


@blends.route('/BatchInventory', methods=['GET', 'POST'])
@login_required
def Batch_Inventory():
    # Import necessary libraries
    import datetime
    from sqlalchemy import func
    from sqlalchemy.orm import aliased

    # Define aliases for the tables
    InventoryVirginBatchAlias = aliased(InventoryVirginBatch)
    MaterialsTableAlias = aliased(MaterialsTable)

    # Initialize batch_id_set as an empty set
    batch_id_set = set()

    # Retrieve the blend inventory data where CurrentWeight > 5
    query = db.session.query(
        InventoryVirginBatchAlias.BatchID,
        MaterialsTableAlias.MaterialName,
        MaterialsTableAlias.SupplierProduct,  # Include SupplierProduct in the query
        InventoryVirginBatchAlias.CurrentWeight,
        InventoryVirginBatchAlias.BatchTimeStamp    
    ).join(
        MaterialsTableAlias, InventoryVirginBatchAlias.ProductID == MaterialsTableAlias.ProductID
    ).filter(
        InventoryVirginBatchAlias.CurrentWeight > 5  # Add the filter condition
    ).order_by(MaterialsTableAlias.MaterialName)
    
    # Fetch the batch inventory data
    inventory_data = query.all()

    # Create a list to store the result data
    result_data = []

    # Variables for subtotal calculation
    current_material = None
    subtotal_weight = 0

    # Iterate over the inventory data
    for batch_id, material_name, supplier_product, current_weight, batch_date in inventory_data:
        # Check if the material has changed
        if material_name != current_material:
            # Add subtotal row for previous material
            if current_material is not None:
                subtotal_row = ("Subtotal", current_material, supplier_product, subtotal_weight)
                result_data.append(subtotal_row)

            # Update current material and reset subtotal weight
            current_material = material_name
            subtotal_weight = 0

        # Check if batch_date is not None before converting to datetime.date object
        if batch_date is not None:
            batch_date = datetime.datetime.strptime(batch_date, '%Y-%m-%d %H:%M:%S').date()

            batch_row = (batch_id, material_name, supplier_product, current_weight)
            result_data.append(batch_row)

            # Update subtotal weight
            if current_weight is not None:
                subtotal_weight += current_weight

            # Add batch ID to set
            batch_id_set.add(batch_id)

    # Add final subtotal row for the last material
    if current_material is not None:
        subtotal_row = ("Subtotal", current_material, supplier_product, round(subtotal_weight, 2))
        result_data.append(subtotal_row)

    # Calculate total weight
    total_weight = sum(row[3] for row in result_data if isinstance(row[3], (int, float)))

    # Get distinct material names
    material_names = sorted(set(row[1] for row in result_data))

    # Filter by selected material name
    selected_material = request.form.get('material') or request.args.get('material')
    if selected_material and selected_material != "All Materials":
        filtered_data = [row for row in result_data if row[1] == selected_material]
    else:
        filtered_data = result_data

    return render_template(
        "batch_inventory.html",
        user=current_user,
        inventory_query=filtered_data,
        alloy_names=alloy_names,
        total_weight=total_weight,
        selected_alloy=selected_alloy
    )
