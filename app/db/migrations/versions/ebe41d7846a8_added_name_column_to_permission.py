"""Added name column to permission

Revision ID: ebe41d7846a8
Revises: 0f695d6a8b69
Create Date: 2023-03-03 20:25:03.360777

"""
from alembic import op
import sqlalchemy as sa


revision = 'ebe41d7846a8'
down_revision = '0f695d6a8b69'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('permissions', sa.Column('name', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('permissions', 'name')
    # ### end Alembic commands ###