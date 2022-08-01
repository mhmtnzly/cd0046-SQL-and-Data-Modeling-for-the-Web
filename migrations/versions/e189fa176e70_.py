"""empty message

Revision ID: e189fa176e70
Revises: 316a22151bda
Create Date: 2022-07-31 14:53:22.388283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e189fa176e70'
down_revision = '316a22151bda'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.drop_column('Artist', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###
