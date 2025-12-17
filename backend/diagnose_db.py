#!/usr/bin/env python3
"""
Script de diagnóstico para la base de datos
"""

import sys
import os
sys.path.append('.')

from app.database import engine
from sqlalchemy import text

def diagnose_database():
    print('🔍 DIAGNÓSTICO DE BASE DE DATOS')
    print('=' * 50)

    try:
        with engine.connect() as conn:
            # Check tables
            tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in tables_result.fetchall()]
            print(f'📋 Tablas existentes: {tables}')

            if 'siniestros' in tables:
                print('✅ Tabla siniestros existe')

                # Check columns
                columns_result = conn.execute(text('PRAGMA table_info(siniestros)'))
                columns = [(row[1], row[2]) for row in columns_result.fetchall()]
                print(f'📊 Columnas en siniestros ({len(columns)}):')
                for col_name, col_type in columns:
                    print(f'  - {col_name}: {col_type}')

                # Check siniestro count
                count_result = conn.execute(text('SELECT COUNT(*) FROM siniestros'))
                count = count_result.fetchone()[0]
                print(f'📈 Registros en siniestros: {count}')

                if count > 0:
                    # Get first siniestro
                    siniestro_result = conn.execute(text('SELECT id, reclamo_num, compania_seguros FROM siniestros LIMIT 1'))
                    siniestro = siniestro_result.fetchone()
                    siniestro_id = siniestro[0]
                    print(f'🆔 Primer siniestro: ID={siniestro_id}, Reclamo={siniestro[1]}, Compañía={siniestro[2]}')

                    # Check related tables
                    related_tables = ['asegurados', 'beneficiarios', 'conductores', 'objetos_asegurados',
                                    'antecedentes', 'relatos_asegurado', 'relatos_conductor', 'inspecciones', 'testigos']

                    for table in related_tables:
                        if table in tables:
                            try:
                                table_count_result = conn.execute(text(f'SELECT COUNT(*) FROM {table} WHERE siniestro_id = ?'), (siniestro_id,))
                                table_count = table_count_result.fetchone()[0]
                                print(f'  └─ {table}: {table_count} registros')
                            except Exception as e:
                                print(f'  └─ {table}: ❌ ERROR - {e}')
                        else:
                            print(f'  └─ {table}: ❌ TABLA NO EXISTE')
                else:
                    print('⚠️ No hay siniestros en la base de datos')
            else:
                print('❌ Tabla siniestros no existe')

    except Exception as e:
        print(f'❌ Error de BD: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    diagnose_database()
