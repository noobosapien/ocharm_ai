"""3

Revision ID: 8ae57b17356c
Revises: ae64d9e5eac6
Create Date: 2025-01-21 09:44:07.891812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ae57b17356c'
down_revision: Union[str, None] = 'ae64d9e5eac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('primary_user', sa.Integer(), nullable=True))
    op.drop_constraint('user_product_line_id_fkey', 'user', type_='foreignkey')
    op.create_foreign_key(None, 'user', 'user', ['primary_user'], ['id'])
    op.drop_column('user', 'product_line_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('product_line_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.create_foreign_key('user_product_line_id_fkey', 'user', 'user', ['product_line_id'], ['id'])
    op.drop_column('user', 'primary_user')
    # ### end Alembic commands ###
