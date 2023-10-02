from flask_login import UserMixin
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import validates

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
        PrimaryKeyConstraint('BlendID', 'PartID', name='BlendPartID'),
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
    
    # class Maintenance(db.Model):
    #     __tablename__ = 'maintenance'
    #     ID = db.Column(db.Integer, primary_key=True)
    #     Work_Order = db.Column(db.String(50))
    #     Created_On = db.Column(db.DateTime, default=datetime.utcnow)
    #     Due_Date = db.Column(db.DateTime)
    #     Next_Due_Date = db.Column(db.DateTime)
    #     End_Due_Date = db.Column(db.DateTime)
    #     Updated_On = db.Column(db.DateTime, default=datetime.utcnow)
    #     Completed_On = db.Column(db.DateTime)
    #     Work_Order_Title = db.Column(db.String(100))
    #     Work_Order_Description = db.Column(db.String(500))
    #     Additional_Cost = db.Column(db.Float)
    #     Labor_Cost = db.Column(db.Float)
    #     Parts_Cost = db.Column(db.Float)
    #     Total_Cost = db.Column(db.Float)
    #     Time = db.Column(db.Float)
    #     Status = db.Column(db.String(20))
    #     Category = db.Column(db.String(50))
    #     Reschedule_Based_On_Completion = db.Column(db.Boolean)
    #     Repeating_Schedule = db.Column(db.Boolean)
    #     Root_Work_Order_Exists = db.Column(db.Boolean)
    #     Asset_ID = db.Column(db.Integer)
    #     Asset_Name = db.Column(db.String(100))
    #     Asset_Category = db.Column(db.String(50))
    #     Asset_Area = db.Column(db.String(50))
    #     Asset_Barcode = db.Column(db.String(50))
    #     Location_Name = db.Column(db.String(100))
    #     Location_Address = db.Column(db.String(200))
    #     Location_ID = db.Column(db.Integer)
    #     Completed_By = db.Column(db.String(100))
    #     Completed_By_ID = db.Column(db.Integer)
    #     Requires_Signature = db.Column(db.Boolean)
    #     Signature_Image = db.Column(db.String(200))
    #     Assigned_By = db.Column(db.String(100))
    #     Assigned_By_ID = db.Column(db.Integer)
    #     Assigned_To = db.Column(db.String(100))
    #     Assigned_To_ID = db.Column(db.Integer)
    #     Team_Assigned = db.Column(db.String(100))
    #     Team_Assigned_ID = db.Column(db.Integer)
    #     Parts = db.Column(db.String(500))
    #     Purchase_Orders = db.Column(db.String(500))
    #     Estimated_Duration = db.Column(db.Float)
    #     Updates = db.Column(db.String(500))
    #     Priority = db.Column(db.String(20))
    #     Archived_Status = db.Column(db.Boolean)
    #     Images = db.Column(db.String(500))
    #     Checklist_ID = db.Column(db.Integer)
    #     Task_Data = db.Column(db.String(500))
    #     Task_Images = db.Column(db.String(500))
    #     Additional_Workers = db.Column(db.String(500))
    #     Additional_Worker_IDs = db.Column(db.String(500))
    #     Requested_By = db.Column(db.String(100))
    #     Requested_By_ID = db.Column(db.Integer)
    #     Requested_By_Email_Address = db.Column(db.String(100))
    #     Part_IDs = db.Column(db.String(500))
    #     Part_Quantities = db.Column(db.String(500))
    #     File_IDs = db.Column(db.String(500))

    
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
