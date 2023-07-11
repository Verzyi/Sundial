from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import func
from datetime import datetime
from sqlalchemy import ForeignKeyConstraint




class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

class PowderBlendParts(db.Model):
    PartID = db.Column(db.Integer, primary_key=True, nullable=False) 
    BlendID = db.Column(db.Integer)
    PartBlendID = db.Column(db.Integer)
    PartBatchID = db.Column(db.Integer)
    AddedWeight = db.Column(db.Float)


class InventoryVirginBatch(db.Model):
    BatchID = db.Column(db.Integer, primary_key=True, nullable=False) 
    BatchCreatedBy = db.Column(db.Integer)
    BatchTimeStamp = db.Column(db.String)
    BatchFacilityID = db.Column(db.Integer)
    ProductID = db.Column(db.Integer)
    VirginPO = db.Column(db.Integer)
    VirginLot = db.Column(db.String)
    VirginQty = db.Column(db.Float)
    

class MaterialsTable(db.Model):
    MaterialName = db.Column(db.String(50))
    SupplierProduct = db.Column(db.String, primary_key=True, unique=True)
    MaterialID = db.Column(db.Integer)
    ProductID = db.Column(db.Integer)    


class PowderBlends(db.Model):
    BlendID	= db.Column(db.Integer, primary_key=True)
    BlendDate = db.Column(db.String)
    BlendCreatedBy	= db.Column(db.Integer)
    MaterialID	=db.Column(db.Integer)
    TotalWeight = db.Column(db.Float)
    CurrentWeight = db.Column(db.Float)


class PowderBlendCalc(db.Model):
    BlendID = db.Column(db.Integer, primary_key=True)	
    PartID = db.Column(db.Integer, primary_key=True)
    PartWeight	= db.Column(db.Float)
    PartFraction = db.Column(db.Float)	
    SieveCount = db.Column(db.Integer)
    
    
__table_args__ = (
        ForeignKeyConstraint(['BlendID', 'PartID'], ['PowderBlends.BlendID', 'PowderBlendParts.PartID']),
    )

class BuildsTable(db.Model):
    BuildIt = db.Column(db.Integer, primary_key=True)
    CreatedBy = db.Column(db.Integer)
    CreatedOn = db.Column(db.String)
    FacilityName = db.Column(db.String)
    SJBuild = db.Column(db.Integer)
    Material = db.Column(db.String)
    MachineID = db.Column(db.String)
    BuildName = db.Column(db.String)
    PlatformWeight = db.Column(db.Float)
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
    FinishPlatformWeight = db.Column(db.Float)
    BlendID = db.Column(db.Integer)
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
    ParameterRev = db.Column(db.Integer)
    MeasuredLaserPower = db.Column(db.Integer)
    GasFlow = db.Column(db.Integer)
    MaterialAdded = db.Column(db.Boolean)
    InitialDosingFactor = db.Column(db.Float)
    MaxFinishHeight = db.Column(db.Integer)
    MaxBuildTime = db.Column(db.Integer)
    MaxDateDifference = db.Column(db.Integer)
    PlatformTemperature = db.Column(db.Integer)
    StartLaserHours = db.Column(db.Integer)
    FinalLaserHours = db.Column(db.Integer)
    InertTime = db.Column(db.Integer)
    F9FilterSerial = db.Column(db.String)
    H13FilterSerial = db.Column(db.String)
    FilterLight = db.Column(db.String)
    EndPartPistonHeight = db.Column(db.Integer)
    Breakout = db.Column(db.Integer)
    CompletedWithoutStoppage = db.Column(db.Boolean)
    Humidity = db.Column(db.Integer)
    BuildInterrupts = db.Column(db.Boolean)
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
    BeamStabilityTestPerformed = db.Column(db.Boolean)
    LaserAlignmentTestPerformed = db.Column(db.Boolean)
    ThermalSensorTest = db.Column(db.Boolean)
    LaserFocus = db.Column(db.Boolean)
    PowderBed = db.Column(db.Boolean)
    PowderLevel = db.Column(db.Boolean)
    SieveLife = db.Column(db.Integer)
    FilterPressureDrop = db.Column(db.Integer)
    Platform = db.Column(db.String)
    BuildType = db.Column(db.String)

