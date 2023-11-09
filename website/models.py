from flask_login import UserMixin
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.orm import validates ,relationship



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
    BatchID = db.Column(db.Integer, primary_key=True) 
    BatchCreatedBy = db.Column(db.Integer)
    BatchTimeStamp = db.Column(db.String)
    BatchFacilityID = db.Column(db.Integer)
    ProductID = db.Column(db.Integer)
    VirginPO = db.Column(db.String) # Must be string to allow old cases where there are multiple POs for a single Batch
    VirginLot = db.Column(db.String)
    VirginWeight = db.Column(db.Float)
    CurrentWeight = db.Column(db.Float)

class PowderBlends(db.Model):
    BlendID	= db.Column(db.Integer, primary_key=True, unique=True)
    BlendDate = db.Column(db.String)
    BlendCreatedBy = db.Column(db.Integer)
    AlloyID	= db.Column(db.Integer, nullable=True)
    TotalWeight = db.Column(db.Float)
    CurrentWeight = db.Column(db.Float)
    
class PowderBlendParts(db.Model):
    PartID = db.Column(db.Integer, primary_key=True) 
    BlendID = db.Column(db.Integer)
    PartBlendID = db.Column(db.Integer, nullable=True)
    PartBatchID = db.Column(db.Integer, nullable=True)
    AddedWeight = db.Column(db.Float)

class PowderBlendCalc(db.Model):
    __table_args__ = (
        PrimaryKeyConstraint('BlendID', 'PartID', name='pk_blend_part'),
        # ForeignKeyConstraint(['BlendID', 'PartID'], ['powder_blend_parts.BlendID', 'powder_blend_parts.PartID']),
    )
    BlendID = db.Column(db.Integer, primary_key=True, unique=False)	
    PartID = db.Column(db.Integer, primary_key=True, unique=False)
    PartWeight = db.Column(db.Float)
    PartFraction = db.Column(db.Float)	
    SieveCount = db.Column(db.Integer)

class BuildsTable(db.Model):
    BuildID = db.Column(db.Integer, primary_key=True)
    CreatedBy = db.Column(db.Integer)
    CreatedOn = db.Column(db.String)
    FacilityName = db.Column(db.String)
    SJBuild = db.Column(db.Integer)
    AlloyName = db.Column(db.String)
    MachineID = db.Column(db.String)
    BuildName = db.Column(db.String)
    PlateWeight = db.Column(db.Float)
    Layer = db.Column(db.Float)
    BuildHeight = db.Column(db.Float)
    Offset = db.Column(db.Float)
    ScaleX = db.Column(db.Float)
    ScaleY = db.Column(db.Float)
    Notes = db.Column(db.String)
    BuildStartTime = db.Column(db.String, nullable=True)
    BuildFinishTime = db.Column(db.String, nullable=True)
    BuildTime = db.Column(db.Float)
    FinishHeight = db.Column(db.Float)
    FinishPlateWeight = db.Column(db.Float)
    BlendID = db.Column(db.Integer)
    CertificationBuild = db.Column(db.Boolean)
    FeedPowderHeight = db.Column(db.Float)
    EndFeedPowderHeight = db.Column(db.Float)
    PotentialBuildHeight = db.Column(db.Float)
    Location = db.Column(db.Integer)
    PlateThickness = db.Column(db.Float)
    PlateSerial = db.Column(db.String)
    MinChargeAmount = db.Column(db.Integer)
    MaxChargeAmount = db.Column(db.Integer)
    DosingBoostAmount = db.Column(db.Integer)
    RecoaterSpeed = db.Column(db.Integer)
    ParameterRev = db.Column(db.String)
    MeasuredLaserPower = db.Column(db.Integer)
    GasFlow = db.Column(db.Float)
    MaterialAdded = db.Column(db.Boolean)
    InitialDosingFactor = db.Column(db.Integer)
    MaxFinishHeight = db.Column(db.Integer)
    MaxBuildTime = db.Column(db.Integer)
    MaxDateDifference = db.Column(db.Integer)
    PlateTemperature = db.Column(db.Float)
    StartLaserHours = db.Column(db.Integer)
    FinalLaserHours = db.Column(db.Integer)
    InertTime = db.Column(db.String, nullable=True)
    F9FilterSerial = db.Column(db.String)
    H13FilterSerial = db.Column(db.String)
    FilterLight = db.Column(db.Boolean)
    EndPartPistonHeight = db.Column(db.Float)
    BreakoutTime = db.Column(db.String, nullable=True)
    CompletedWithoutStoppage = db.Column(db.Boolean)
    Humidity = db.Column(db.Float)
    BuildInterrupts = db.Column(db.Boolean)
    RecoaterType = db.Column(db.String)
    VeloFlowSoftwareRev = db.Column(db.String)
    VeloFlowSoftwareBase = db.Column(db.String)
    VeloFlowBuildTime = db.Column(db.Float)
    VeloFlowBuildTimeCore = db.Column(db.Float)
    VeloFlowBuildTimeSkin = db.Column(db.Integer)
    VeloFlowBuildTimeSupport = db.Column(db.Integer)
    VeloFlowBuildTimeRecoater = db.Column(db.Integer)
    VeloPrintSWRev = db.Column(db.Float)
    SieveChange = db.Column(db.Boolean)
    LayerCount = db.Column(db.Integer)
    FilterChange = db.Column(db.Boolean)
    BeamStabilityTestPerformed = db.Column(db.Boolean)
    LaserAlignmentTestPerformed = db.Column(db.Boolean)
    ThermalSensorTest = db.Column(db.Boolean)
    LaserFocus = db.Column(db.Boolean)
    PowderBed = db.Column(db.Boolean)
    PowderLevel = db.Column(db.Float)
    SieveLife = db.Column(db.Float)
    FilterPressureDrop = db.Column(db.Float)
    Platform = db.Column(db.String)
    BuildType = db.Column(db.String)
    
   

    
    date_cols = ['BuildStart', 'BuildFinish', 'InertTime', 'BreakoutTime']
    for col in date_cols:
        @validates(col)
        def empty_string_to_null(self, key, value):
            if (value == 'NaT') or (value == ''):
                return None
            else:
                return value
    
    def to_dict(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }
class Machines(db.Model):
    MachineID = db.Column(db.Integer, primary_key=True)
    MachineSerial = db.Column(db.Integer)
    LocationID = db.Column(db.Integer, ForeignKey('location.LocationID'))  # Foreign key relationship
    MachineName = db.Column(db.String(50))
    MachineAlias = db.Column(db.String(50))
    MachineType = db.Column(db.String(50))

    # Establish a relationship with the Location table
    location = relationship('Location', back_populates='machines')

class Location(db.Model):
    LocationID = db.Column(db.Integer, primary_key=True)
    LocationName = db.Column(db.String(50))
    LocationAlias = db.Column(db.String(50))

    # Establish a relationship with the Machines table
    machines = relationship('Machines', back_populates='location')
    
    
# class Scale(db.Model):
#     ScaleID = db.column(db.Integer, primary_key = True)
#     FileName = db.column(db.String(50))
#     UserID = db.column(db.Integer,ForeignKey('users.id'))
#     DateCreated = db.Column(db.String, nullable=True)
#     AlloyID = db.column(db.Integer, ForeignKey('materialAlloys.AlloyID'))  # Foreign key relationship
#     MachineID = db.Column(db.Integer, ForeignKey('machines.MachineID'))  # Foreign key relationship
#     CaliperAssetNo = db.column(db.String(50))
#     InputX = db.column(db.Float)
#     InputY = db.column(db.Float)
#     InputOffset = db.column(db.Float)
#     NewX = db.column(db.Float)
#     NewY = db.column(db.Float)
#     NewOffset = db.column(db.Float)
    
    
    
