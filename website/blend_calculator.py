
from . import db
from .models import PowderBlends, MaterialsTable, InventoryVirginBatch, PowderBlendParts, PowderBlendCalc, BuildsTable

class BlendDatabaseUpdater:
    def __init__(self, blend_limit=500, frac_limit=0.0001):
        self.blend_limit = blend_limit
        self.frac_limit = frac_limit

    def update_blend_database(self, blend_numbers, blend_weights,db):
        count = 0
        start = db.session.query(PowderBlendCalc).order_by(PowderBlendCalc.BlendID.desc()).first()
        if start is None:
            start = 0
        else:
            start = start.BlendID

        blend_list = set(blend_numbers)

        for blend_id in blend_list:
            blend_parts = db.session.query(PowderBlendParts).filter(PowderBlendParts.BlendID == blend_id).all()
            for blend_part in blend_parts:
                part_id = blend_part.PartID
                old_blend = blend_part.PartBlendID
                batch = blend_part.PartBatchID
                weight = blend_part.AddedWeight

                frac = self.calculate_fraction(blend_id, part_id, weight)

                sieve_count = 1

                if old_blend is None:
                    new_row = PowderBlendCalc(BlendID=blend_id, PartID=part_id, PartWeight=weight,
                                              PartFraction=frac, SieveCount=sieve_count)
                    db.session.add(new_row)
                else:
                    part_blend_rows = db.session.query(PowderBlendCalc).filter(PowderBlendCalc.BlendID == old_blend).all()
                    for part_blend_row in part_blend_rows:
                        if weight is not None and part_blend_row.PartFraction is not None:##added this so that it would work need to look this over tomorrow 
                            part_id2 = part_blend_row.PartBlendID
                            batch2 = self.get_batch_id(old_blend, part_id2)
                            frac2 = part_blend_row.PartFraction
                            weight2 = frac2 * weight
                            frac3 = frac2 * frac
                            sieve_count2 = part_blend_row.SieveCount + 1

                            if frac3 <= self.frac_limit:
                                continue

                            new_row = PowderBlendCalc(BlendID=blend_id, PartBlendID=part_id2, PartWeight=weight2,
                                                    PartFraction=frac3, SieveCount=sieve_count2)
                            db.session.add(new_row)

            count += 1
            if count >= self.blend_limit:
                break

        db.session.commit()

    def calculate_fraction(self, blend_id, part_id, weight):
        total_weight = db.session.query(PowderBlends.TotalWeight).filter(PowderBlends.BlendID == blend_id).first()
        if total_weight is None:
            return 0.0

        total_weight = total_weight[0]
        if total_weight == 0:
            return 0.0

        part_weight = db.session.query(PowderBlendParts.AddedWeight).filter(
            PowderBlendParts.BlendID == blend_id, PowderBlendParts.PartID == part_id).first()
        if part_weight is None:
            return 0.0

        part_weight = part_weight[0]
        if part_weight == 0:
            return 0.0

        return weight / total_weight * part_weight

    def get_batch_id(self, blend_id, part_id):
        batch_id = db.session.query(PowderBlendParts.PartBatchID).filter(
            PowderBlendParts.BlendID == blend_id, PowderBlendParts.PartID == part_id).first()
        if batch_id is None:
            return None

        return batch_id[0]
