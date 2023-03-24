"""Fuck it

Revision ID: 7719290aceaa
Revises: 64f348dffd26
Create Date: 2023-03-04 22:32:44.723566

"""
from alembic import op
import sqlalchemy as sa


revision = '7719290aceaa'
down_revision = '64f348dffd26'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('users_seller_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'seller_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('seller_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key('users_seller_id_fkey', 'users', 'sellers', ['seller_id'], ['id'])
    # ### end Alembic commands ###