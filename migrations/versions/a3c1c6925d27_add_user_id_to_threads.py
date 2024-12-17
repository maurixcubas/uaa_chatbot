"""Add user_id to threads

Revision ID: a3c1c6925d27
Revises: 
Create Date: 2024-12-17 14:48:17.066622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3c1c6925d27'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('thread', schema=None) as batch_op:
        batch_op.add_column(sa.Column('openai_thread_id', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('thread', schema=None) as batch_op:
        batch_op.drop_column('openai_thread_id')

    # ### end Alembic commands ###