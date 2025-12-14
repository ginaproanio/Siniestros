"""initial_migration

Revision ID: initial_migration
Revises:
Create Date: 2025-12-13 21:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create all tables from scratch - clean database schema

    # Create siniestros table
    op.create_table('siniestros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('compania_seguros', sa.String(length=255), nullable=False),
        sa.Column('reclamo_num', sa.String(length=100), nullable=False),
        sa.Column('fecha_siniestro', sa.DateTime(timezone=True), nullable=False),
        sa.Column('direccion_siniestro', sa.String(length=500), nullable=False),
        sa.Column('ubicacion_geo_lat', sa.Float(), nullable=True),
        sa.Column('ubicacion_geo_lng', sa.Float(), nullable=True),
        sa.Column('danos_terceros', sa.Boolean(), nullable=True),
        sa.Column('ejecutivo_cargo', sa.String(length=255), nullable=True),
        sa.Column('fecha_designacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tipo_siniestro', sa.String(length=100), nullable=True),
        sa.Column('fecha_reportado', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cobertura', sa.String(length=100), nullable=True),
        sa.Column('pdf_firmado_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reclamo_num')
    )

    # Create asegurados table
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

    # Create beneficiarios table
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

    # Create conductores table
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

    # Create objetos_asegurados table
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

    # Create antecedentes table
    op.create_table('antecedentes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create relatos_asegurado table
    op.create_table('relatos_asegurado',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('numero_relato', sa.Integer(), nullable=False),
        sa.Column('texto', sa.Text(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create inspecciones table
    op.create_table('inspecciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('numero_inspeccion', sa.Integer(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create testigos table
    op.create_table('testigos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('numero_relato', sa.Integer(), nullable=False),
        sa.Column('texto', sa.Text(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create visitas_taller table
    op.create_table('visitas_taller',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )

    # Create dinamicas_accidente table
    op.create_table('dinamicas_accidente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('siniestro_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['siniestro_id'], ['siniestros.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('siniestro_id')
    )


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('dinamicas_accidente')
    op.drop_table('visitas_taller')
    op.drop_table('testigos')
    op.drop_table('inspecciones')
    op.drop_table('relatos_asegurado')
    op.drop_table('antecedentes')
    op.drop_table('objetos_asegurados')
    op.drop_table('conductores')
    op.drop_table('beneficiarios')
    op.drop_table('asegurados')
    op.drop_table('siniestros')
