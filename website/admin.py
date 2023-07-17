from flask_admin.contrib.sqla import ModelView

def configure_admin(admin, db):
    from .models import Users, PowderBlendParts, InventoryVirginBatch, MaterialsTable, PowderBlends, PowderBlendCalc, BuildsTable
    admin.add_view(ModelView(Users, db.session, category="Users"))
    admin.add_view(ModelView(PowderBlendParts, db.session, category="Blend"))
    admin.add_view(ModelView(InventoryVirginBatch, db.session, category="Blend"))
    admin.add_view(ModelView(MaterialsTable, db.session, category="Blend"))
    admin.add_view(ModelView(PowderBlends, db.session, category="Blend"))
    admin.add_view(ModelView(PowderBlendCalc, db.session, category="Blend"))
    admin.add_view(ModelView(BuildsTable, db.session, category="Build"))
