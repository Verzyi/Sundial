"""empty message

Revision ID: 4e63a069b954
Revises: 1513ff3283f7
Create Date: 2023-11-28 15:43:04.993321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e63a069b954'
down_revision = '1513ff3283f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ncrs_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('CreatedOn', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('CreatedBy', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_ncr_user', 'users', ['CreatedBy'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ncrs_table', schema=None) as batch_op:
        batch_op.drop_constraint('fk_ncr_user', type_='foreignkey')
        batch_op.drop_column('CreatedBy')
        batch_op.drop_column('CreatedOn')

    # ### end Alembic commands ###
