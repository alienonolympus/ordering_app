"""empty message

Revision ID: 83b1d122887e
Revises: 8ae19666bc12
Create Date: 2018-10-06 13:47:38.119161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83b1d122887e'
down_revision = '8ae19666bc12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('full_name', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('tutor_group', sa.String(length=8), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'tutor_group')
    op.drop_column('user', 'full_name')
    # ### end Alembic commands ###