"""Added ProducTags

Revision ID: 84a0107276ed
Revises: 802ac1d20267
Create Date: 2023-03-08 12:18:32.806821

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '84a0107276ed'
down_revision = '802ac1d20267'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_tags',
    sa.Column('product_id', sa.BigInteger(), nullable=False),
    sa.Column('parent_tag_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=72), nullable=True),
    sa.Column('short_description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['parent_tag_id'], ['product_tags.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_tags_id'), 'product_tags', ['id'], unique=True)
    op.drop_index('ix_tags_id', table_name='tags')
    op.drop_table('tags')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=72), autoincrement=False, nullable=True),
    sa.Column('short_description', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('parent_tag_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['parent_tag_id'], ['tags.id'], name='tags_parent_tag_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='tags_pkey')
    )
    op.create_index('ix_tags_id', 'tags', ['id'], unique=False)
    op.drop_index(op.f('ix_product_tags_id'), table_name='product_tags')
    op.drop_table('product_tags')
    # ### end Alembic commands ###