def generate_report(blend_id, output_format):
    # Get the blend information
    blend = PowderBlends.query.get(blend_id)
    if blend is None:
        return 'Blend not found'

    # Get the blend parts information
    blend_parts = PowderBlendParts.query.filter_by(BlendID=blend_id).all()

    # Get the inventory virgin batch information
    batch_ids = [part.PartBatchID for part in blend_parts]
    virgin_batches = InventoryVirginBatch.query.filter(InventoryVirginBatch.BatchID.in_(batch_ids)).all()

    # Get the materials information
    material_ids = [blend.MaterialID for blend in blend_parts]
    materials = MaterialsTable.query.filter(MaterialsTable.MaterialID.in_(material_ids)).all()

    # Process the data and create the required variables for the report
    blend_summary = {
        'Blend': blend.BlendID,
        'Material': materials[0].MaterialName if materials else '',
        'Total Weight (kg)': blend.TotalWeight,
        'Avg. Sieve Count': 0,
        'Max. Sieve Count': 0
    }

    majority_batch = {
        'BatchID': '',
        'Supplier Product': '',
        'Purchase Order': '',
        'Virgin Lot': '',
        'Percent': 0,
        'Sieve Count': 0
    }

    blend_breakdown = []

    # Calculate the average and maximum sieve count
    sieve_counts = []
    for part in blend_parts:
        sieve_count = PowderBlendCalc.query.filter_by(BlendID=blend_id, PartID=part.PartID).first()
        if sieve_count:
            sieve_counts.append(sieve_count.SieveCount)

    if sieve_counts:
        blend_summary['Avg. Sieve Count'] = sum(sieve_counts) / len(sieve_counts)
        blend_summary['Max. Sieve Count'] = max(sieve_counts)

    # Generate the breakdown information
    for part in blend_parts:
        batch = next((b for b in virgin_batches if b.BatchID == part.PartBatchID), None)
        material = next((m for m in materials if m.MaterialID == part.MaterialID), None)

        if batch and material:
            breakdown_entry = {
                'BatchID': batch.BatchID,
                'Supplier Product': material.SupplierProduct,
                'Purchase Order': batch.VirginPO,
                'Virgin Lot': batch.VirginLot,
                'Percent': part.AddedWeight / blend.TotalWeight * 100,
                'Sieve Count': 0
            }

            sieve_count = PowderBlendCalc.query.filter_by(BlendID=blend_id, PartID=part.PartID).first()
            if sieve_count:
                breakdown_entry['Sieve Count'] = sieve_count.SieveCount

            blend_breakdown.append(breakdown_entry)

    # Render the report template
    env = Environment(loader=PackageLoader(__name__))
    template = env.get_template('report.html')
    rendered_report = template.render(
        blend_summary=blend_summary,
        majority_batch=majority_batch,
        blend_breakdown=blend_breakdown
    )

    # Generate the report in the requested format
    if output_format == 'html':
        return rendered_report
    elif output_format == 'pdf':
        pdf = HTML(string=rendered_report).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=blend_report.pdf'
        return response
    else:
        return 'Invalid output format'


