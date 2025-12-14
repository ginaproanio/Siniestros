"""Add new fields for siniestro declaration and investigation

Revision ID: add_new_declaration_fields
Revises: 8716f86c2a3f
Create Date: 2025-12-13 17:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_new_declaration_fields'
down_revision: Union[str, None] = '8716f86c2a3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns for siniestro declaration
    op.add_column('siniestros', sa.Column('fecha_declaracion', sa.DateTime(timezone=True), nullable=True))
    op.add_column('siniestros', sa.Column('persona_declara_tipo', sa.String(length=20), nullable=True))
    op.add_column('siniestros', sa.Column('persona_declara_cedula', sa.String(length=20), nullable=True))
    op.add_column('siniestros', sa.Column('persona_declara_nombre', sa.String(length=255), nullable=True))
    op.add_column('siniestros', sa.Column('persona_declara_relacion', sa.String(length=255), nullable=True))

    # Add misiva de investigación column
    op.add_column('siniestros', sa.Column('misiva_investigacion', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove the new columns
    op.drop_column('siniestros', 'misiva_investigacion')
    op.drop_column('siniestros', 'persona_declara_relacion')
    op.drop_column('siniestros', 'persona_declara_nombre')
    op.drop_column('siniestros', 'persona_declara_cedula')
    op.drop_column('siniestros', 'persona_declara_tipo')
    op.drop_column('siniestros', 'fecha_declaracion')
