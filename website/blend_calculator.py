from . import db
from .models import PowderBlends, PowderBlendParts, PowderBlendCalc

class BlendDatabaseUpdater:
    def __init__(self, blend_limit=500, frac_limit=0.0001):
        self.blend_limit = blend_limit
        self.frac_limit = frac_limit
        self.db = db

    def update_blend_database(self, blend_numbers, blend_weights):
        total_weight = sum(float(weight) for weight in blend_weights)
        blend_fractions = [float(weight) / total_weight for weight in blend_weights]
        last_blend = PowderBlends.query.order_by(PowderBlends.BlendID.desc()).first()
        last_blend_id = last_blend.BlendID if last_blend else 0

        for i, blend_number in enumerate(blend_numbers):
            part_blend_id = i + 1
            part_weight = blend_weights[i]
            part_fraction = blend_fractions[i]
            sieve_count = 0

            for blend_part in PowderBlendParts.query.filter_by(BlendID=blend_number):
                part_id = blend_part.PartID
                old_blend = blend_part.PartBlendID
                weight = blend_part.AddedWeight

                frac = self.calculate_fraction(blend_number, part_id, weight)

                if old_blend is None:
                    new_row = PowderBlendCalc(
                        BlendID=last_blend_id,
                        PartID=part_id,
                        PartWeight=part_weight,
                        PartFraction=frac,
                        SieveCount=sieve_count,
                    )
                    self.db.session.add(new_row)
                else:
                    part_blend_rows = PowderBlendCalc.query.filter_by(BlendID=old_blend).all()
                    for part_blend_row in part_blend_rows:
                        part_id2 = part_blend_row.PartID
                        frac2 = part_blend_row.PartFraction
                        weight2 = frac2 * weight if frac2 is not None else None
                        frac3 = frac2 * frac if frac2 is not None else None
                        sieve_count2 = part_blend_row.SieveCount + 1

                        if frac3 is not None and frac3 <= self.frac_limit:
                            continue

                        new_row = PowderBlendCalc(
                            BlendID=last_blend_id + 1,
                            PartID=part_id2,
                            PartWeight=weight2,
                            PartFraction=frac3,
                            SieveCount=sieve_count2,
                        )
                        self.db.session.add(new_row)

        self.db.session.commit()
        print("Blend calculations updated successfully.")

    def calculate_fraction(self, blend_id, part_id, weight):
        total_weight = PowderBlends.query.with_entities(PowderBlends.TotalWeight).filter_by(BlendID=blend_id).scalar()
        if total_weight is None or total_weight == 0:
            return 0.0

        part_weight = PowderBlendParts.query.with_entities(PowderBlendParts.AddedWeight).filter_by(
            BlendID=blend_id, PartID=part_id).scalar()
        if part_weight is None or part_weight == 0:
            return 0.0

        return weight / total_weight * part_weight








# from . import db
# from .models import PowderBlends, PowderBlendParts, PowderBlendCalc

# class BlendDatabaseUpdater:
#     def __init__(self, blend_limit=500, frac_limit=0.0001):
#         self.blend_limit = blend_limit
#         self.frac_limit = frac_limit

#     def update_blend_database(self, blend_numbers, blend_weights):
#         # Calculate the blend fractions
#         total_weight = sum(float(weight) for weight in blend_weights)
#         blend_fractions = [float(weight) / total_weight for weight in blend_weights]

#         # Retrieve the last blend ID from the database
#         last_blend = PowderBlends.query.order_by(PowderBlends.BlendID.desc()).first()
#         last_blend_id = last_blend.BlendID if last_blend else 0

#         # Update the PowderBlendCalc table
#         for i, blend_number in enumerate(blend_numbers):
#             part_blend_id = i + 1
#             part_weight = blend_weights[i]
#             part_fraction = blend_fractions[i]
#             sieve_count = 0

#             # Create a new PowderBlendCalc record
#             new_blend_calc = PowderBlendCalc(
#                 BlendID=last_blend_id + 1,
#                 PartID=part_blend_id,
#                 PartWeight=part_weight,
#                 PartFraction=part_fraction,
#                 SieveCount=sieve_count,
#             )
#             db.session.add(new_blend_calc)

#         db.session.commit()

#         # Print the updated blend calculations
#         print("Blend calculations updated successfully.")