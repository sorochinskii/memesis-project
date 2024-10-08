"""Memes model add delete mark

Revision ID: 2dda52148012
Revises: ff56ad57778b
Create Date: 2024-07-19 16:25:03.390137

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2dda52148012'
down_revision: Union[str, None] = 'ff56ad57778b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('memes', sa.Column(
        'delete_mark', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('memes', 'delete_mark')
    # ### end Alembic commands ###
