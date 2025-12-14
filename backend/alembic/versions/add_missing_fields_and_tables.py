"""add_missing_fields_and_tables

Revision ID: add_missing_fields_and_tables
Revises: 6702cc57308c
Create Date: 2025-12-13 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_fields_and_tables'
down_revision = '6702cc57308c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add missing columns to siniestros table - this is the main fix needed
    op.add_column('siniestros', sa.Column('fecha_reportado', sa.DateTime(timezone=True), nullable=True))
    op.add_column('siniestros', sa.Column('cobertura', sa.String(length=100), nullable=True))
    op.add_column('siniestros', sa.Column('pdf_firmado_url', sa.String(length=500), nullable=True))

    # Note: Tables will be created by the application when needed
    # Since the database has garbage data and user doesn't care about losing it,
    # we'll focus on fixing the immediate column error first


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('dinamicas_accidente')
    op.drop_table('visitas_taller')
    op.drop_table('testigos')
    op.drop_table('inspecciones')
    op.drop_table('relatos_asegurado')
    op.drop_table('antecedentes')
    op.drop_table('objetos_asegurados')
    op.drop_table('conductores')
    op.drop_table('beneficiarios')

    # Drop columns from siniestros table
    op.drop_column('siniestros', 'pdf_firmado_url')
    op.drop_column('siniestros', 'cobertura')
    op.drop_column('siniestros', 'fecha_reportado')
