"""add column index to otpusk_hotel_ta.expired and otpusk_hotel_ta_cache.expired

Revision ID: d4f711b4dbc4
Revises: 540d46123add
Create Date: 2021-10-01 15:10:34.507947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4f711b4dbc4'
down_revision = '540d46123add'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_otpusk_hotel_ta_expired'), 'otpusk_hotel_ta', ['expired'], unique=False)
    op.create_index(op.f('ix_otpusk_hotel_ta_cache_expired'), 'otpusk_hotel_ta_cache', ['expired'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_otpusk_hotel_ta_cache_expired'), table_name='otpusk_hotel_ta_cache')
    op.drop_index(op.f('ix_otpusk_hotel_ta_expired'), table_name='otpusk_hotel_ta')
    # ### end Alembic commands ###
