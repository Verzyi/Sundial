"""empty message

Revision ID: c4c5cac010ee
Revises: 
Create Date: 2023-10-16 16:10:44.457856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4c5cac010ee'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('location',
    sa.Column('LocationID', sa.Integer(), nullable=False),
    sa.Column('LocationName', sa.String(length=50), nullable=True),
    sa.Column('LocationAlias', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('LocationID')
    )
    op.create_table('machines',
    sa.Column('MachineID', sa.Integer(), nullable=False),
    sa.Column('MachineSerial', sa.Integer(), nullable=True),
    sa.Column('LocationID', sa.Integer(), nullable=True),
    sa.Column('MachineName', sa.String(length=50), nullable=True),
    sa.Column('MachineAlias', sa.String(length=50), nullable=True),
    sa.Column('MachineType', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('MachineID')
    )
    op.create_table('schedule_tasks',
    sa.Column('ScheduleID', sa.Integer(), nullable=False),
    sa.Column('TaskID', sa.Integer(), nullable=True),
    sa.Column('TaskOrder', sa.Integer(), nullable=True),
    sa.Column('MachineID', sa.Integer(), nullable=True),
    sa.Column('AlloyID', sa.Integer(), nullable=True),
    sa.Column('TaskAssignmentStart', sa.String(), nullable=True),
    sa.Column('TaskAssignmentFinish', sa.String(), nullable=True),
    sa.Column('TaskAssignmentLength', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('ScheduleID')
    )
    op.create_table('task_types',
    sa.Column('TaskTypeID', sa.Integer(), nullable=False),
    sa.Column('TaskTypeName', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('TaskTypeID')
    )
    op.create_table('tasks',
    sa.Column('TaskID', sa.Integer(), nullable=False),
    sa.Column('TaskTypeID', sa.Integer(), nullable=True),
    sa.Column('TaskName', sa.String(length=50), nullable=True),
    sa.Column('TaskEstimateLength', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('TaskID')
    )
    with op.batch_alter_table('builds_table', schema=None) as batch_op:
        batch_op.alter_column('BuildID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('CreatedBy',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('CreatedOn',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('FacilityName',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('SJBuild',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('AlloyName',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('MachineID',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BuildName',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('Notes',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BuildStartTime',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BuildFinishTime',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BlendID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('Location',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('PlateSerial',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('MinChargeAmount',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('MaxChargeAmount',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('DosingBoostAmount',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('RecoaterSpeed',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('ParameterRev',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('MeasuredLaserPower',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('InitialDosingFactor',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('MaxFinishHeight',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('MaxBuildTime',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('MaxDateDifference',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('StartLaserHours',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('FinalLaserHours',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('InertTime',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('F9FilterSerial',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('H13FilterSerial',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BreakoutTime',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('RecoaterType',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowSoftwareRev',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowSoftwareBase',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowBuildTimeSkin',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowBuildTimeSupport',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowBuildTimeRecoater',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('LayerCount',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('Platform',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BuildType',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)

    with op.batch_alter_table('inventory_virgin_batch', schema=None) as batch_op:
        batch_op.alter_column('BatchID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('BatchCreatedBy',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('BatchTimeStamp',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BatchFacilityID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('ProductID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('VirginPO',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('VirginLot',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)

    with op.batch_alter_table('material_alloys', schema=None) as batch_op:
        batch_op.alter_column('AlloyID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('Alloy',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('MaterialName',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('MaterialID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('AlloyName',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.create_unique_constraint(None, ['AlloyID'])

    with op.batch_alter_table('material_products', schema=None) as batch_op:
        batch_op.alter_column('ProductID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('SupplierProduct',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('AlloyID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.create_unique_constraint(None, ['ProductID'])

    with op.batch_alter_table('powder_blend_calc', schema=None) as batch_op:
        batch_op.alter_column('BlendID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False)
        batch_op.alter_column('PartID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False)
        batch_op.alter_column('SieveCount',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)

    with op.batch_alter_table('powder_blend_parts', schema=None) as batch_op:
        batch_op.alter_column('PartID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('BlendID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('PartBlendID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('PartBatchID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)

    with op.batch_alter_table('powder_blends', schema=None) as batch_op:
        batch_op.alter_column('BlendID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('BlendDate',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('BlendCreatedBy',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('AlloyID',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.create_unique_constraint(None, ['BlendID'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('email',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('password',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('first_name',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('last_name',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('role',
               existing_type=sa.TEXT(),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.create_unique_constraint(None, ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('role',
               existing_type=sa.String(length=10),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('last_name',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('first_name',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('password',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('powder_blends', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('AlloyID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BlendCreatedBy',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BlendDate',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('BlendID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('powder_blend_parts', schema=None) as batch_op:
        batch_op.alter_column('PartBatchID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('PartBlendID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BlendID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('PartID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('powder_blend_calc', schema=None) as batch_op:
        batch_op.alter_column('SieveCount',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('PartID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True)
        batch_op.alter_column('BlendID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True)

    with op.batch_alter_table('material_products', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('AlloyID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('SupplierProduct',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('ProductID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('material_alloys', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('AlloyName',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('MaterialID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('MaterialName',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('Alloy',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('AlloyID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('inventory_virgin_batch', schema=None) as batch_op:
        batch_op.alter_column('VirginLot',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('VirginPO',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('ProductID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BatchFacilityID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BatchTimeStamp',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('BatchCreatedBy',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BatchID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('builds_table', schema=None) as batch_op:
        batch_op.alter_column('BuildType',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('Platform',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('LayerCount',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowBuildTimeRecoater',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowBuildTimeSupport',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowBuildTimeSkin',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowSoftwareBase',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('VeloFlowSoftwareRev',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('RecoaterType',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('BreakoutTime',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('H13FilterSerial',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('F9FilterSerial',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('InertTime',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('FinalLaserHours',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('StartLaserHours',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('MaxDateDifference',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('MaxBuildTime',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('MaxFinishHeight',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('InitialDosingFactor',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('MeasuredLaserPower',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('ParameterRev',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('RecoaterSpeed',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('DosingBoostAmount',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('MaxChargeAmount',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('MinChargeAmount',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('PlateSerial',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('Location',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BlendID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BuildFinishTime',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('BuildStartTime',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('Notes',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('BuildName',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('MachineID',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('AlloyName',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('SJBuild',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('FacilityName',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('CreatedOn',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('CreatedBy',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=True)
        batch_op.alter_column('BuildID',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               nullable=True,
               autoincrement=True)

    op.drop_table('tasks')
    op.drop_table('task_types')
    op.drop_table('schedule_tasks')
    op.drop_table('machines')
    op.drop_table('location')
    # ### end Alembic commands ###
