"""add TourCategory, TourTransport, TourFood, TourLength, TourFrom

Revision ID: c5be1599145a
Revises: f765e4aa9a1b
Create Date: 2021-06-01 14:24:24.580031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5be1599145a'
down_revision = 'f765e4aa9a1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tour_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('order_index', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.Column('selected', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('value', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tour_food',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('order_index', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.Column('selected', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('value', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tour_from',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('order_index', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.Column('selected', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tour_length',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('order_index', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.Column('selected', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('nights_from', sa.Integer(), nullable=False),
    sa.Column('nights_to', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tour_transport',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('order_index', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.Column('selected', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('value', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    conn = op.get_bind()

    conn.execute("INSERT INTO tour_category (id, name, order_index, selected, value) VALUES (1, 'Любая', 1, 1, 'any')")
    conn.execute("INSERT INTO tour_category (id, name, order_index, selected, value) VALUES (2, '2* и выше', 2, 0, '5,4,3,2')")
    conn.execute("INSERT INTO tour_category (id, name, order_index, selected, value) VALUES (3, '3* и выше', 3, 0, '5,4,3')")
    conn.execute("INSERT INTO tour_category (id, name, order_index, selected, value) VALUES (4, '4* и выше', 4, 0, '5,4')")
    conn.execute("INSERT INTO tour_category (id, name, order_index, selected, value) VALUES (5, 'только 5*', 5, 0, '5')")

    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (1, 'Любое', 1, 0, 'any')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (2, 'OB', 2, 0, 'ob')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (3, 'BB', 3, 0, 'bb')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (4, 'HB', 4, 0, 'hb')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (5, 'FB', 5, 0, 'fb')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (6, 'AI', 6, 0, 'ai')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (7, 'UAI', 7, 0, 'uai')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (8, 'BB и лучше', 8, 1, 'bb,hb,fb,ai,uai')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (9, 'HB и лучше', 9, 0, 'hb,fb,ai,uai')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (10, 'FB и лучше', 10, 0, 'fb,ai,uai')")
    conn.execute("INSERT INTO tour_food (id, name, order_index, selected, value) VALUES (11, 'AI и UAI', 11, 0, 'ai,uai')")

    conn.execute("INSERT INTO tour_from (id, name, order_index, selected, value) VALUES (1, 'Киев', 1, 0, 1544)")
    conn.execute("INSERT INTO tour_from (id, name, order_index, selected, value) VALUES (2, 'Днепропетровск', 2, 0, 1874)")
    conn.execute("INSERT INTO tour_from (id, name, order_index, selected, value) VALUES (3, 'Запопрожье', 3, 0, 1875)")
    conn.execute("INSERT INTO tour_from (id, name, order_index, selected, value) VALUES (4, 'Львов', 4, 1, 1397)")
    conn.execute("INSERT INTO tour_from (id, name, order_index, selected, value) VALUES (5, 'Одесса', 5, 0, 1358)")
    conn.execute("INSERT INTO tour_from (id, name, order_index, selected, value) VALUES (6, 'Харьков', 6, 0, 1880)")

    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (1, '1-3 ночи', 1, 0, 1, 3)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (2, '2-4 ночи', 2, 0, 2, 4)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (3, '3-5 ночей', 3, 0, 3, 5)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (4, '4-6 ночей', 4, 0, 4, 6)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (5, '5-7 ночей', 5, 0, 5, 7)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (6, '6-8 ночей', 6, 0, 6, 8)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (7, '7-9 ночей', 7, 1, 7, 9)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (8, '8-10 ночей', 8, 0, 8, 10)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (9, '9-11 ночей', 9, 0, 9, 11)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (10, '10-12 ночей', 10, 0, 10, 12)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (11, '11-13 ночей', 11, 0, 11, 13)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (12, '12-14 ночей', 12, 0, 12, 14)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (13, '13-15 ночей', 13, 0, 13, 15)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (14, '14-16 ночей', 14, 0, 14, 16)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (15, '15-17 ночей', 15, 0, 15, 17)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (16, '16-18 ночей', 16, 0, 16, 18)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (17, '17-19 ночей', 17, 0, 17, 19)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (18, '18-20 ночей', 18, 0, 18, 20)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (19, '19-21 ночь', 19, 0, 19, 21)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (20, '20-22 ночи', 20, 0, 20, 22)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (21, '21-23 ночи', 21, 0, 21, 23)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (22, '22-24 ночи', 22, 0, 22, 24)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (23, '23-25 ночей', 23, 0, 23, 25)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (24, '24-26 ночей', 24, 0, 24, 26)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (25, '25-27 ночей', 25, 0, 25, 27)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (26, '26-28 ночей', 26, 0, 26, 28)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (27, '27-29 ночей', 27, 0, 27, 29)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (28, '28-30 ночей', 28, 0, 28, 30)")
    conn.execute("INSERT INTO tour_length (id, name, order_index, selected, nights_from, nights_to) VALUES (29, '30 ночей', 29, 0, 30, 32)")

    conn.execute("INSERT INTO tour_transport (id, name, order_index, selected, value) VALUES (1, 'Любой', 1, 0, 'any')")
    conn.execute("INSERT INTO tour_transport (id, name, order_index, selected, value) VALUES (2, 'Авиаперелет', 2, 1, 'air')")
    conn.execute("INSERT INTO tour_transport (id, name, order_index, selected, value) VALUES (3, 'Автобус', 3, 0, 'bus')")
    conn.execute("INSERT INTO tour_transport (id, name, order_index, selected, value) VALUES (4, 'Поезд', 4, 0, 'train')")
    conn.execute("INSERT INTO tour_transport (id, name, order_index, selected, value) VALUES (5, 'Судно', 5, 0, 'ship')")
    conn.execute("INSERT INTO tour_transport (id, name, order_index, selected, value) VALUES (6, 'Транспорт не включён', 6, 0, 'no')")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tour_transport')
    op.drop_table('tour_length')
    op.drop_table('tour_from')
    op.drop_table('tour_food')
    op.drop_table('tour_category')
    # ### end Alembic commands ###
