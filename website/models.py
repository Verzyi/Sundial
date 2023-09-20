from flask_login import UserMixin
from sqlalchemy import ForeignKeyConstraint

from . import db


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(10), default='User')
    # ip = db.Column(db.String(50))

class MaterialProducts(db.Model):
    ProductID = db.Column(db.Integer, primary_key=True, unique=True)
    SupplierProduct = db.Column(db.String)
    AlloyID = db.Column(db.Integer)

class MaterialAlloys(db.Model):
    AlloyID = db.Column(db.Integer, primary_key=True, unique=True)
    Alloy = db.Column(db.String)
    MaterialName = db.Column(db.String(50))
    MaterialID = db.Column(db.Integer)
    AlloyName = db.Column(db.String(50))

class InventoryVirginBatch(db.Model):
    BatchID = db.Column(db.Integer, primary_key=True, nullable=False) 
    BatchCreatedBy = db.Column(db.Integer)
    BatchTimeStamp = db.Column(db.String)
    BatchFacilityID = db.Column(db.Integer)
    ProductID = db.Column(db.Integer)
    VirginPO = db.Column(db.String) # Must be string to allow old cases where there are multiple POs for a single Batch
    VirginLot = db.Column(db.String)
    VirginWeight = db.Column(db.Float)
    CurrentWeight = db.Column(db.Float)

class PowderBlends(db.Model):
    BlendID	= db.Column(db.Integer, primary_key=True, unique=True )
    BlendDate = db.Column(db.String)
    BlendCreatedBy = db.Column(db.Integer)
    AlloyID	= db.Column(db.Integer, nullable=True)
    TotalWeight = db.Column(db.Float)
    CurrentWeight = db.Column(db.Float)
    
__table_args__ = (
    ForeignKeyConstraint(
        ['BlendID', 'PartID'], 
        ['PowderBlends.BlendID', 'PowderBlendParts.PartID']
        ),
    )

class PowderBlendCalc(db.Model):
    BlendID = db.Column(db.Integer, primary_key=True)	
    PartID = db.Column(db.Integer, primary_key=True)
    PartWeight = db.Column(db.Float)
    PartFraction = db.Column(db.Float)	
    SieveCount = db.Column(db.Integer)
    
class PowderBlendParts(db.Model):
    PartID = db.Column(db.Integer, primary_key=True, nullable=False) 
    BlendID = db.Column(db.Integer)
    PartBlendID = db.Column(db.Integer, nullable=True)
    PartBatchID = db.Column(db.Integer, nullable=True)
    AddedWeight = db.Column(db.Float)

class BuildsTable(db.Model):
    BuildIt = db.Column(db.Integer, primary_key=True)
    CreatedBy = db.Column(db.Integer)
    CreatedOn = db.Column(db.String)
    FacilityName = db.Column(db.String)
    SJBuild = db.Column(db.Integer)
    AlloyName = db.Column(db.String)
    MachineID = db.Column(db.String)
    BuildName = db.Column(db.String)
    PlateWeight = db.Column(db.Float)
    Layer = db.Column(db.Float)
    Height = db.Column(db.Float)
    Offset = db.Column(db.Float)
    ScaleX = db.Column(db.Float)
    ScaleY = db.Column(db.Float)
    Note = db.Column(db.String)
    BuildStart = db.Column(db.String)
    BuildFinish = db.Column(db.String)
    BuildTime = db.Column(db.Integer)
    FinishHeight = db.Column(db.Integer)
    FinishPlateWeight = db.Column(db.Float)
    BlendID = db.Column(db.Integer, nullable=True)
    CertificationBuild = db.Column(db.Boolean)
    FeedPowderHeight = db.Column(db.Float)
    EndFeedPowderHeight = db.Column(db.Float)
    PotentialBuildHeight = db.Column(db.Float)
    Location = db.Column(db.String)
    PlateThickness = db.Column(db.Integer)
    PlateSerial = db.Column(db.String)
    MinChargeAmount = db.Column(db.Integer)
    MaxChargeAmount = db.Column(db.Integer)
    DosingBoostAmount = db.Column(db.Float)
    RecoaterSpeed = db.Column(db.Integer)
    ParameterRev = db.Column(db.String)
    MeasuredLaserPower = db.Column(db.Integer)
    GasFlow = db.Column(db.Integer)
    MaterialAdded = db.Column(db.String)
    InitialDosingFactor = db.Column(db.Float)
    MaxFinishHeight = db.Column(db.Integer)
    MaxBuildTime = db.Column(db.Integer)
    MaxDateDifference = db.Column(db.Integer)
    PlateTemperature = db.Column(db.Integer)
    StartLaserHours = db.Column(db.Integer)
    FinalLaserHours = db.Column(db.Integer)
    InertTime = db.Column(db.Integer)
    F9FilterSerial = db.Column(db.String)
    H13FilterSerial = db.Column(db.String)
    FilterLight = db.Column(db.String)
    EndPartPistonHeight = db.Column(db.Integer)
    Breakout = db.Column(db.Integer)
    CompletedWithoutStoppage = db.Column(db.String)
    Humidity = db.Column(db.Integer)
    BuildInterrupts = db.Column(db.String)
    RecoaterType = db.Column(db.String)
    VeloFlowSoftwareRev = db.Column(db.String)
    VeloFlowSoftwareBase = db.Column(db.String)
    VeloFlowBuildTimeEstimation = db.Column(db.String)
    VeloFlowBuildTimeEstimationCore = db.Column(db.String)
    VeloFlowBuildTimeEstimationSkin = db.Column(db.String)
    VeloFlowBuildTimeEstimationSupport = db.Column(db.String)
    VeloFlowBuildTimeEstimationRecoater = db.Column(db.String)
    VeloPrintSWRev = db.Column(db.String)
    SieveChange = db.Column(db.Integer)
    LayerCount = db.Column(db.Integer)
    FilterChange = db.Column(db.Integer)
    BeamStabilityTestPerformed = db.Column(db.String)
    LaserAlignmentTestPerformed = db.Column(db.String)
    ThermalSensorTest = db.Column(db.String)
    LaserFocus = db.Column(db.String)
    PowderBed = db.Column(db.String)
    PowderLevel = db.Column(db.Float)
    SieveLife = db.Column(db.Float)
    FilterPressureDrop = db.Column(db.Float)
    Platform = db.Column(db.String)
    BuildType = db.Column(db.String)
    
    def to_dict(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }