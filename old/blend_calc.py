from ..website import db
from ..website.models import PowderBlends, PowderBlendCalc


class BlendCalcUpdater:
    def __init__(self, blend_limit=500, frac_limit=0.0001):
        self.blend_limit = blend_limit
        self.frac_limit = frac_limit
        self.db = db

    def UpdatePowderBlendCalc(self, blend_numbers, blend_weights):
        blend_fractions = []
        blend_part_ids = []
        calculated_weights = []
        sieve_counts = []

        for blend_number in blend_numbers:
            total_weight = sum(float(weight) for weight in blend_weights)

            fractions = PowderBlendCalc.query.with_entities(PowderBlendCalc.PartFraction) \
                .filter_by(BlendID=blend_number) \
                .all()
            blend_fractions.extend([float(frac.PartFraction) for frac in fractions])

            part_ids = PowderBlendCalc.query.with_entities(PowderBlendCalc.PartID) \
                .filter_by(BlendID=blend_number) \
                .all()
            blend_part_ids.extend([part_id.PartID for part_id in part_ids])

            calculated_weights.extend([frac * total_weight for frac in blend_fractions])

            sieve_counts.extend([count.SieveCount + 1 for count in PowderBlendCalc.query.with_entities(
                PowderBlendCalc.SieveCount).filter_by(BlendID=blend_number)])

        last_blend = PowderBlends.query.order_by(PowderBlends.BlendID.desc()).first()
        last_blend_id = int(last_blend.BlendID) if last_blend else 0

        for i, blend_number in enumerate(blend_part_ids):
            part_weight = calculated_weights[i]
            blend_part_id = blend_part_ids[i]
            part_fraction = blend_fractions[i]
            sieve_count = sieve_counts[i]

            new_row = PowderBlendCalc(
                BlendID=last_blend_id,
                PartID=blend_part_id,
                PartWeight=part_weight,
                PartFraction=part_fraction,
                SieveCount=sieve_count,
            )
            self.db.session.add(new_row)

        self.db.session.commit()
        print('Blend calculations updated successfully.')
