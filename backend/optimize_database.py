"""
Database Optimization Script

Adds indexes and optimizes database performance for the siniestros system.
Run this script to improve query performance and data integrity.
"""

from sqlalchemy import create_engine, text, Index, MetaData
from app.database import SQLALCHEMY_DATABASE_URL
from app.models import siniestro

def optimize_database():
    """Add performance indexes and optimize database"""

    print("🚀 Iniciando optimización de base de datos...")

    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Check if indexes already exist to avoid errors
            existing_indexes = conn.execute(text("""
                SELECT indexname FROM pg_indexes
                WHERE tablename IN ('siniestros', 'asegurados', 'conductores', 'objetos_asegurados')
            """)).fetchall()

            existing_index_names = [idx[0] for idx in existing_indexes]

            print(f"📊 Encontrados {len(existing_index_names)} índices existentes")

            # Performance indexes for siniestros table
            indexes_to_create = [
                # Date-based indexes for filtering
                ("ix_siniestros_fecha_siniestro", "siniestros", ["fecha_siniestro"]),
                ("ix_siniestros_fecha_reportado", "siniestros", ["fecha_reportado"]),
                ("ix_siniestros_fecha_designacion", "siniestros", ["fecha_designacion"]),
                ("ix_siniestros_created_at", "siniestros", ["created_at"]),
                ("ix_siniestros_updated_at", "siniestros", ["updated_at"]),

                # Category-based indexes for filtering
                ("ix_siniestros_tipo_siniestro", "siniestros", ["tipo_siniestro"]),
                ("ix_siniestros_compania_seguros", "siniestros", ["compania_seguros"]),
                ("ix_siniestros_tipo_reclamo", "siniestros", ["tipo_reclamo"]),

                # Foreign key indexes (already exist but good to verify)
                ("ix_asegurados_siniestro_id", "asegurados", ["siniestro_id"]),
                ("ix_beneficiarios_siniestro_id", "beneficiarios", ["siniestro_id"]),
                ("ix_conductores_siniestro_id", "conductores", ["siniestro_id"]),
                ("ix_objetos_asegurados_siniestro_id", "objetos_asegurados", ["siniestro_id"]),
                ("ix_visitas_taller_siniestro_id", "visitas_taller", ["siniestro_id"]),
                ("ix_dinamicas_accidente_siniestro_id", "dinamicas_accidente", ["siniestro_id"]),
                ("ix_antecedentes_siniestro_id", "antecedentes", ["siniestro_id"]),
                ("ix_relatos_asegurado_siniestro_id", "relatos_asegurado", ["siniestro_id"]),
                ("ix_relatos_conductor_siniestro_id", "relatos_conductor", ["siniestro_id"]),
                ("ix_inspecciones_siniestro_id", "inspecciones", ["siniestro_id"]),
                ("ix_testigos_siniestro_id", "testigos", ["siniestro_id"]),

                # Composite indexes for common queries
                ("ix_siniestros_compania_fecha", "siniestros", ["compania_seguros", "fecha_siniestro"]),
                ("ix_siniestros_tipo_fecha", "siniestros", ["tipo_siniestro", "fecha_siniestro"]),
                ("ix_siniestros_reclamo_fecha", "siniestros", ["tipo_reclamo", "fecha_siniestro"]),

                # Text search indexes for full-text search
                ("ix_siniestros_direccion_gin", "siniestros", None, "CREATE INDEX ix_siniestros_direccion_gin ON siniestros USING gin(to_tsvector('spanish', direccion_siniestro))"),
                ("ix_siniestros_reclamo_num_gin", "siniestros", None, "CREATE INDEX ix_siniestros_reclamo_num_gin ON siniestros USING gin(to_tsvector('spanish', reclamo_num))"),
            ]

            created_indexes = 0

            for index_name, table_name, columns, custom_sql in indexes_to_create:
                if custom_sql:
                    # Custom index (like GIN for full-text search)
                    if index_name not in existing_index_names:
                        try:
                            conn.execute(text(custom_sql))
                            conn.commit()
                            print(f"✅ Creado índice personalizado: {index_name}")
                            created_indexes += 1
                        except Exception as e:
                            print(f"⚠️ Error creando índice personalizado {index_name}: {e}")
                else:
                    # Standard B-tree index
                    if index_name not in existing_index_names:
                        try:
                            index_sql = f"CREATE INDEX {index_name} ON {table_name} ({', '.join(columns)})"
                            conn.execute(text(index_sql))
                            conn.commit()
                            print(f"✅ Creado índice: {index_name}")
                            created_indexes += 1
                        except Exception as e:
                            print(f"⚠️ Error creando índice {index_name}: {e}")

            # Add check constraints for data integrity
            constraints_to_add = [
                ("chk_siniestros_lat", "siniestros", "ubicacion_geo_lat >= -90 AND ubicacion_geo_lat <= 90"),
                ("chk_siniestros_lng", "siniestros", "ubicacion_geo_lng >= -180 AND ubicacion_geo_lng <= 180"),
                ("chk_siniestros_tipo_persona", "siniestros", "persona_declara_tipo IN ('asegurado', 'conductor', 'broker', 'otro')"),
                ("chk_objetos_asegurados_ano", "objetos_asegurados", "ano >= 1900 AND ano <= 2030"),
            ]

            created_constraints = 0

            for constraint_name, table_name, constraint_sql in constraints_to_add:
                try:
                    # Check if constraint exists
                    constraint_exists = conn.execute(text(f"""
                        SELECT 1 FROM information_schema.table_constraints
                        WHERE constraint_name = '{constraint_name}'
                        AND table_name = '{table_name}'
                    """)).fetchone()

                    if not constraint_exists:
                        add_constraint_sql = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} CHECK ({constraint_sql})"
                        conn.execute(text(add_constraint_sql))
                        conn.commit()
                        print(f"✅ Agregada restricción: {constraint_name}")
                        created_constraints += 1
                    else:
                        print(f"ℹ️ Restricción ya existe: {constraint_name}")

                except Exception as e:
                    print(f"⚠️ Error agregando restricción {constraint_name}: {e}")

            print("\n🎉 Optimización completada:")
            print(f"   📊 Índices creados: {created_indexes}")
            print(f"   🔒 Restricciones agregadas: {created_constraints}")
            print("\n💡 Recomendaciones adicionales:")
            print("   • Monitorear performance con EXPLAIN ANALYZE")
            print("   • Considerar particionamiento si hay muchos registros")
            print("   • Configurar autovacuum para mantenimiento automático")

        except Exception as e:
            print(f"❌ Error durante optimización: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    optimize_database()
