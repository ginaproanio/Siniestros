from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.SiniestroResponse)
async def create_siniestro(siniestro: schemas.SiniestroCreate, db: Session = Depends(get_db)):
    """Crear un nuevo siniestro"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info("🚀 Iniciando creación de siniestro")
    logger.info(f"📋 Datos recibidos: {siniestro.model_dump()}")

    try:
        # Check if reclamo_num already exists
        db_siniestro = db.query(models.Siniestro).filter(models.Siniestro.reclamo_num == siniestro.reclamo_num).first()
        if db_siniestro:
            logger.warning(f"⚠️ Número de reclamo ya existe: {siniestro.reclamo_num}")
            raise HTTPException(status_code=400, detail="Número de reclamo ya existe")

        logger.info("✅ Validación de reclamo_num pasada")

        # Crear el siniestro
        siniestro_data = siniestro.model_dump()
        logger.info(f"📝 Creando siniestro con datos: {siniestro_data}")

        db_siniestro = models.Siniestro(**siniestro_data)
        db.add(db_siniestro)

        logger.info("💾 Guardando en base de datos...")
        db.commit()
        db.refresh(db_siniestro)

        logger.info(f"✅ Siniestro creado exitosamente con ID: {db_siniestro.id}")
        return db_siniestro

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al crear siniestro: {e}")
        logger.error(f"❌ Tipo de error: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/", response_model=List[schemas.SiniestroResponse])
async def get_siniestros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todos los siniestros con paginación"""
    siniestros = db.query(models.Siniestro).offset(skip).limit(limit).all()
    return siniestros

@router.get("/{siniestro_id}", response_model=schemas.SiniestroFullResponse)
async def get_siniestro(siniestro_id: int, db: Session = Depends(get_db)):
    """Obtener un siniestro completo por ID con todas sus relaciones"""
    siniestro = db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    if not siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")
    return siniestro

@router.put("/{siniestro_id}", response_model=schemas.SiniestroResponse)
async def update_siniestro(siniestro_id: int, siniestro_update: schemas.SiniestroUpdate, db: Session = Depends(get_db)):
    """Actualizar un siniestro"""
    db_siniestro = db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    if not db_siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")

    update_data = siniestro_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_siniestro, field, value)

    db.commit()
    db.refresh(db_siniestro)
    return db_siniestro

@router.delete("/{siniestro_id}")
async def delete_siniestro(siniestro_id: int, db: Session = Depends(get_db)):
    """Eliminar un siniestro"""
    db_siniestro = db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    if not db_siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")

    db.delete(db_siniestro)
    db.commit()
    return {"message": "Siniestro eliminado exitosamente"}

# Additional endpoints for related entities
@router.post("/{siniestro_id}/asegurado", response_model=schemas.AseguradoResponse)
async def create_asegurado(siniestro_id: int, asegurado: schemas.AseguradoCreate, db: Session = Depends(get_db)):
    """Crear asegurado para un siniestro"""
    db_asegurado = models.Asegurado(siniestro_id=siniestro_id, **asegurado.model_dump())
    db.add(db_asegurado)
    db.commit()
    db.refresh(db_asegurado)
    return db_asegurado

@router.post("/{siniestro_id}/relato-asegurado", response_model=schemas.RelatoAseguradoResponse)
async def create_relato_asegurado(siniestro_id: int, relato: schemas.RelatoAseguradoCreate, db: Session = Depends(get_db)):
    """Crear relato del asegurado"""
    # Get the next numero_relato
    max_num = db.query(models.RelatoAsegurado).filter(models.RelatoAsegurado.siniestro_id == siniestro_id).count()
    numero_relato = max_num + 1

    db_relato = models.RelatoAsegurado(siniestro_id=siniestro_id, numero_relato=numero_relato, **relato.model_dump())
    db.add(db_relato)
    db.commit()
    db.refresh(db_relato)
    return db_relato

# Similar endpoints for other entities...
@router.post("/{siniestro_id}/inspeccion", response_model=schemas.InspeccionResponse)
async def create_inspeccion(siniestro_id: int, inspeccion: schemas.InspeccionCreate, db: Session = Depends(get_db)):
    """Crear inspección del lugar del siniestro"""
    max_num = db.query(models.Inspeccion).filter(models.Inspeccion.siniestro_id == siniestro_id).count()
    numero_inspeccion = max_num + 1

    db_inspeccion = models.Inspeccion(siniestro_id=siniestro_id, numero_inspeccion=numero_inspeccion, **inspeccion.model_dump())
    db.add(db_inspeccion)
    db.commit()
    db.refresh(db_inspeccion)
    return db_inspeccion

@router.post("/{siniestro_id}/testigo", response_model=schemas.TestigoResponse)
async def create_testigo(siniestro_id: int, testigo: schemas.TestigoCreate, db: Session = Depends(get_db)):
    """Crear testigo"""
    max_num = db.query(models.Testigo).filter(models.Testigo.siniestro_id == siniestro_id).count()
    numero_relato = max_num + 1

    db_testigo = models.Testigo(siniestro_id=siniestro_id, numero_relato=numero_relato, **testigo.model_dump())
    db.add(db_testigo)
    db.commit()
    db.refresh(db_testigo)
    return db_testigo

# PDF generation endpoint (placeholder for now)
@router.post("/{siniestro_id}/generar-pdf")
async def generar_pdf(siniestro_id: int, db: Session = Depends(get_db)):
    """Generar PDF del informe de siniestro"""
    try:
        from app.utils.pdf_generator import generate_siniestro_pdf
        pdf_data = generate_siniestro_pdf(siniestro_id, db)

        from fastapi.responses import StreamingResponse
        import io

        # Crear respuesta con el PDF
        def iter_pdf():
            yield pdf_data

        return StreamingResponse(
            iter_pdf(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=siniestro_{siniestro_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
