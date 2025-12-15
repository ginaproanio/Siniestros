#!/usr/bin/env python3
"""
Script para crear datos de prueba manualmente en la base de datos
Ejecutar desde el directorio backend: python create_test_data.py
"""
import sys
import os
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app import models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    """Crear datos de prueba completos"""
    logger.info("🧪 CREANDO DATOS DE PRUEBA MANUALMENTE")

    db = SessionLocal()

    try:
        # Verificar si ya existe el siniestro de prueba
        existing = db.query(models.Siniestro).filter(
            models.Siniestro.reclamo_num == "25-01-VH-7079448"
        ).first()

        if existing:
            logger.info(f"✅ Siniestro ya existe con ID: {existing.id}")
            db.close()
            return existing.id

        logger.info("🏗️ Creando siniestro de prueba...")

        # Crear siniestro principal
        siniestro = models.Siniestro(
            compania_seguros="ZURICH SEGUROS ECUADOR S.A.",
            ruc_compania="1791240014001",
            tipo_reclamo="ROBO",
            poliza="3351",
            reclamo_num="25-01-VH-7079448",
            fecha_siniestro=datetime.fromisoformat("2025-11-28T10:49:00"),
            fecha_reportado=datetime.fromisoformat("2025-11-30T10:49:00"),
            direccion_siniestro="Metroparqueos (Sucursal Eloy Alfaro). Pradera y Mariano Aguilera",
            ubicacion_geo_lat=-0.193108,
            ubicacion_geo_lng=-78.486227,
            danos_terceros=False,
            ejecutivo_cargo="",
            fecha_designacion=datetime.fromisoformat("2025-12-12T00:00:00"),
            tipo_siniestro="Vehicular",
            cobertura="Todo riesgo",

            # Nuevos campos de declaración
            fecha_declaracion=datetime.fromisoformat("2025-11-28T10:49:00"),
            persona_declara_tipo="asegurado",
            persona_declara_cedula="2100348008",
            persona_declara_nombre="LANDAZURI MIRANDA PATRICIA VERONI",
            persona_declara_relacion="Propietario del vehículo",

            # Misiva de investigación
            misiva_investigacion="Se solicita investigación completa del accidente vehicular ocurrido en Metroparqueos."
        )

        db.add(siniestro)
        db.commit()
        db.refresh(siniestro)
        logger.info(f"✅ Siniestro creado con ID: {siniestro.id}")

        # Crear asegurado
        asegurado = models.Asegurado(
            siniestro_id=siniestro.id,
            tipo="Natural",  # Natural o Jurídica
            cedula="2100348008",
            nombre="LANDAZURI MIRANDA PATRICIA VERONI",
            celular="0997507161",
            direccion="De los Conquistadores y Juan Leon Mera",
            correo="pverolandazuri@hotmail.com",
            telefono="032947804"
        )
        db.add(asegurado)

        # Crear beneficiario
        beneficiario = models.Beneficiario(
            siniestro_id=siniestro.id,
            razon_social="NOVACREDIT S.A.",
            cedula_ruc="",
            domicilio=""
        )
        db.add(beneficiario)

        # Crear conductor
        conductor = models.Conductor(
            siniestro_id=siniestro.id,
            nombre="Manuel Antonio Carrión Herrera",
            cedula="1105653891",
            celular="0969520800",
            direccion="Gaspar de Villarroel y 6 de Diciembre",
            parentesco="Amigo"
        )
        db.add(conductor)

        # Crear objeto asegurado
        objeto = models.ObjetoAsegurado(
            siniestro_id=siniestro.id,
            placa="PFB4337",
            marca="TOYOTA",
            modelo="Corolla Cross High AC 1.8 5P 4x2",
            tipo="Jeep",
            color="Blanco",
            ano=2023,  # El modelo usa 'ano' no 'anio'
            serie_motor="2ZR2X01895",
            chasis="9BRKZAAGXR0669964"
        )
        db.add(objeto)

        db.commit()
        logger.info("✅ Todos los datos relacionados creados")

        # Verificar creación
        count = db.query(models.Siniestro).count()
        logger.info(f"✅ Total siniestros en BD: {count}")

        return siniestro.id

    except Exception as e:
        logger.error(f"❌ Error creando datos de prueba: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        return None

    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 EJECUTANDO CREACIÓN MANUAL DE DATOS DE PRUEBA")
    siniestro_id = create_test_data()

    if siniestro_id:
        logger.info(f"🎉 ÉXITO: Siniestro creado con ID {siniestro_id}")
        logger.info("💡 Ahora puedes probar la aplicación desde el frontend")
    else:
        logger.error("❌ FALLÓ: No se pudo crear el siniestro")
        sys.exit(1)
