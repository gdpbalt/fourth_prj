"""add table otpusk_hotel_ta_cache

Revision ID: e2badc912e31
Revises: a738023e93d3
Create Date: 2021-09-30 17:23:20.513885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2badc912e31'
down_revision = 'a738023e93d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('otpusk_hotel_ta_cache',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('page', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('expired', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id', 'page')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('otpusk_hotel_ta_cache')
    # ### end Alembic commands ###
