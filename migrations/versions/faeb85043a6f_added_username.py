"""added username

Revision ID: faeb85043a6f
Revises: 2873390b2f1a
Create Date: 2023-09-24 14:10:24.063589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'faeb85043a6f'
down_revision = '2873390b2f1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unique_username_constraint', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('unique_email_constraint', sa.String(length=100), nullable=False))
        batch_op.create_unique_constraint('unique_email_constraint', ['unique_username_constraint'])
        batch_op.create_unique_constraint('unique_email_constraint', ['unique_email_constraint'])
        batch_op.drop_column('email')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.VARCHAR(length=100), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('unique_email_constraint')
        batch_op.drop_column('unique_username_constraint')

    # ### end Alembic commands ###
