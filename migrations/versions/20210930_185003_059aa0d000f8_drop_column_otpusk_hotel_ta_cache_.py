"""drop column otpusk_hotel_ta_cache.content

Revision ID: 059aa0d000f8
Revises: defc1e11bc14
Create Date: 2021-09-30 18:50:03.258634

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '059aa0d000f8'
down_revision = 'defc1e11bc14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('otpusk_hotel_ta_cache', 'content')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otpusk_hotel_ta_cache', sa.Column('content', mysql.TEXT(collation='utf8_bin'), nullable=True))
    # ### end Alembic commands ###
