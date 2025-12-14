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
    # Add missing columns to siniestros table
    op.add_column('siniestros', sa.Column('fecha_reportado', sa.DateTime(timezone=True), nullable=True))
    op.add_column('siniestros', sa.Column('cobertura', sa.String(length=100), nullable=True))
    op.add_column('siniestros', sa.Column('pdf_firmado_url', sa.String(length=500), nullable=True))

    # Create all related tables
    # Asegurados table
    op.create_table('asegurados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('cedula', sa.String(length=20), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=True),
        sa.Column('celular', sa.String(length=20), nullable=True),
        sa.Column('correo', sa.String(length=255), nullable=True),
        sa.Column('direccion', sa.String(length=500), nullable=True),
        sa.Column('parentesco', sa.String(length=100), nullable=True),
        sa.Column('ruc', sa.String(length=20), nullable=True),
        sa.Column('empresa', sa.String(length=255), nullable=True),
        sa.Column('representante_legal', sa.String(length=255), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )

    # Beneficiarios table
    op.create_table('beneficiarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('razon_social', sa.String(length=255), nullable=True),
        sa.Column('cedula_ruc', sa.String(length=20), nullable=True),
        sa.Column('domicilio', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )

    # Conductores table
    op.create_table('conductores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('cedula', sa.String(length=20), nullable=False),
        sa.Column('celular', sa.String(length=20), nullable=True),
        sa.Column('direccion', sa.String(length=500), nullable=True),
        sa.Column('parentesco', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )

    # Objetos asegurados table
    op.create_table('objetos_asegurados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('placa', sa.String(length=20), nullable=False),
        sa.Column('marca', sa.String(length=100), nullable=True),
        sa.Column('modelo', sa.String(length=100), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.Column('ano', sa.Integer(), nullable=True),
        sa.Column('serie_motor', sa.String(length=100), nullable=True),
        sa.Column('chasis', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )

    # Antecedentes table
    op.create_table('antecedentes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Relatos asegurados table
    op.create_table('relatos_asegurado',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('numero_relato', sa.Integer(), nullable=False),
        sa.Column('texto', sa.Text(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Inspecciones table
    op.create_table('inspecciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('numero_inspeccion', sa.Integer(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Testigos table
    op.create_table('testigos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('numero_relato', sa.Integer(), nullable=False),
        sa.Column('texto', sa.Text(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Visitas taller table
    op.create_table('visitas_taller',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )

    # Dinamicas accidente table
    op.create_table('dinamicas_accidente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )


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
