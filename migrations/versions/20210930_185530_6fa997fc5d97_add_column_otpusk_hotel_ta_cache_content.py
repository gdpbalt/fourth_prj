"""add column otpusk_hotel_ta_cache.content

Revision ID: 6fa997fc5d97
Revises: 059aa0d000f8
Create Date: 2021-09-30 18:55:30.172383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fa997fc5d97'
down_revision = '059aa0d000f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otpusk_hotel_ta_cache', sa.Column('content', sa.Text(length=1048576), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('otpusk_hotel_ta_cache', 'content')
    # ### end Alembic commands ###