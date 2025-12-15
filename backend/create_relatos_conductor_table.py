#!/usr/bin/env python3
"""
Script para crear la tabla relatos_conductor en la base de datos.
Ejecutar después de actualizar el modelo.
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def create_relatos_conductor_table():
    """Crear la tabla relatos_conductor si no existe."""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS relatos_conductor (
        id SERIAL PRIMARY KEY,
        siniestro_id INTEGER REFERENCES siniestros(id),
        numero_relato INTEGER NOT NULL,
        texto TEXT NOT NULL,
        imagen_url VARCHAR(500)
    );
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Tabla 'relatos_conductor' creada exitosamente")
    except Exception as e:
        print(f"❌ Error creando tabla 'relatos_conductor': {e}")
        return False

    return True

if __name__ == "__main__":
    print("🔄 Creando tabla 'relatos_conductor'...")
    success = create_relatos_conductor_table()
    if success:
        print("✅ Migración completada exitosamente")
    else:
        print("❌ Migración fallida")
        sys.exit(1)
