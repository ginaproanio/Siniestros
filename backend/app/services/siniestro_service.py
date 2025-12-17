"""
Siniestro Service - Business Logic Layer

Handles all business logic related to siniestros, including CRUD operations,
data validation, and business rules.
"""

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel
from .. import models, schemas
from .s3_service import upload_file_to_s3, download_image_from_url
import logging

logger = logging.getLogger(__name__)


class SiniestroService:
    """Service for siniestro business logic"""

    def __init__(self, db: Session):
        self.db = db

    def create_siniestro(self, siniestro_data: schemas.SiniestroCreate) -> models.Siniestro:
        """Create a new siniestro with validation"""
        # Check if reclamo_num already exists
        existing = self.db.query(models.Siniestro).filter(
            models.Siniestro.reclamo_num == siniestro_data.reclamo_num
        ).first()

        if existing:
            raise ValueError(f"Número de reclamo {siniestro_data.reclamo_num} ya existe")

        # Create siniestro
        db_siniestro = models.Siniestro(**siniestro_data.model_dump())
        self.db.add(db_siniestro)
        self.db.commit()
        self.db.refresh(db_siniestro)

        return db_siniestro

    def get_siniestro(self, siniestro_id: int) -> Optional[models.Siniestro]:
        """Get siniestro by ID with all relationships loaded"""
        from sqlalchemy.orm import selectinload
        return self.db.query(models.Siniestro).options(
            selectinload(models.Siniestro.asegurado),
            selectinload(models.Siniestro.beneficiario),
            selectinload(models.Siniestro.conductor),
            selectinload(models.Siniestro.objeto_asegurado),
            selectinload(models.Siniestro.visita_taller),
            selectinload(models.Siniestro.dinamica_accidente),
            selectinload(models.Siniestro.antecedentes),
            selectinload(models.Siniestro.relatos_asegurado),
            selectinload(models.Siniestro.relatos_conductor),
            selectinload(models.Siniestro.inspecciones),
            selectinload(models.Siniestro.testigos)
        ).filter(models.Siniestro.id == siniestro_id).first()

    def get_siniestros(self, skip: int = 0, limit: int = 100) -> List[models.Siniestro]:
        """Get all siniestros with pagination"""
        return self.db.query(models.Siniestro).offset(skip).limit(limit).all()

    def update_siniestro(self, siniestro_id: int, update_data: schemas.SiniestroUpdate) -> models.Siniestro:
        """Update siniestro with business logic"""
        siniestro = self.get_siniestro(siniestro_id)
        if not siniestro:
            raise ValueError(f"Siniestro {siniestro_id} no encontrado")

        update_dict = update_data.model_dump(exclude_unset=True)

        # Handle JSON fields
        json_fields = [
            "observaciones", "recomendacion_pago_cobertura",
            "conclusiones", "anexo"
        ]

        import json
        for field in json_fields:
            if field in update_dict and isinstance(update_dict[field], list):
                update_dict[field] = json.dumps(update_dict[field])

        # Apply updates
        for key, value in update_dict.items():
            setattr(siniestro, key, value)

        self.db.commit()
        self.db.refresh(siniestro)
        return siniestro

    def update_section(self, siniestro_id: int, section: str, data: Union[List[BaseModel], BaseModel, Any]) -> Dict[str, Any]:
        """Update a specific section of siniestro data

        Accepts Pydantic models directly from FastAPI, maintaining type safety
        while preserving backward compatibility with dict-based calls.
        """
        siniestro = self.get_siniestro(siniestro_id)
        if not siniestro:
            raise ValueError(f"Siniestro {siniestro_id} no encontrado")

        # Handle different section types
        if section == "asegurado":
            return self._update_asegurado(siniestro, data)
        elif section == "conductor":
            return self._update_conductor(siniestro, data)
        elif section == "objeto_asegurado":
            return self._update_objeto_asegurado(siniestro, data)
        elif section in ["antecedentes", "relatos_asegurado", "relatos_conductor",
                        "inspecciones", "testigos"]:
            return self._update_list_section(siniestro, section, data)
        elif section in ["evidencias_complementarias", "otras_diligencias",
                        "detalles_visita_taller", "observaciones",
                        "recomendacion_pago_cobertura", "conclusiones", "anexo"]:
            return self._update_json_section(siniestro, section, data)
        else:
            raise ValueError(f"Sección '{section}' no reconocida")

    def _update_asegurado(self, siniestro: models.Siniestro, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update asegurado data"""
        if siniestro.asegurado:
            for key, value in data.items():
                setattr(siniestro.asegurado, key, value)
        else:
            data["siniestro_id"] = siniestro.id
            db_asegurado = models.Asegurado(**data)
            self.db.add(db_asegurado)

        self.db.commit()
        return {"message": "Asegurado actualizado", "siniestro_id": siniestro.id}

    def _update_conductor(self, siniestro: models.Siniestro, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update conductor data"""
        if siniestro.conductor:
            for key, value in data.items():
                setattr(siniestro.conductor, key, value)
        else:
            data["siniestro_id"] = siniestro.id
            db_conductor = models.Conductor(**data)
            self.db.add(db_conductor)

        self.db.commit()
        return {"message": "Conductor actualizado", "siniestro_id": siniestro.id}

    def _update_objeto_asegurado(self, siniestro: models.Siniestro, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update objeto asegurado data"""
        if siniestro.objeto_asegurado:
            for key, value in data.items():
                setattr(siniestro.objeto_asegurado, key, value)
        else:
            data["siniestro_id"] = siniestro.id
            db_objeto = models.ObjetoAsegurado(**data)
            self.db.add(db_objeto)

        self.db.commit()
        return {"message": "Objeto asegurado actualizado", "siniestro_id": siniestro.id}

    def _update_list_section(self, siniestro: models.Siniestro, section: str, data: Union[List[BaseModel], List[Dict[str, Any]], Any]) -> Dict[str, Any]:
        """Update list-type sections (antecedentes, relatos, etc.)

        Accepts both Pydantic models (from FastAPI) and dictionaries (backward compatibility).
        """
        # Map section names to model classes
        model_map = {
            "antecedentes": models.Antecedente,
            "relatos_asegurado": models.RelatoAsegurado,
            "relatos_conductor": models.RelatoConductor,
            "inspecciones": models.Inspeccion,
            "testigos": models.Testigo
        }

        model_class = model_map.get(section)
        if not model_class:
            raise ValueError(f"Sección '{section}' no válida")

        # Ensure data is a list
        if not isinstance(data, list):
            data = [data] if data else []

        # Clear existing data
        self.db.query(model_class).filter(
            getattr(model_class, 'siniestro_id') == siniestro.id
        ).delete()

        # Add new data
        for item in data:
            # Convert Pydantic model to dict if needed
            if hasattr(item, 'model_dump'):
                item_data = item.model_dump()
            elif isinstance(item, dict):
                item_data = item.copy()
            else:
                raise ValueError(f"Formato de datos no válido para {section}: {type(item)}")

            # Handle image processing for relatos and inspecciones
            if section in ["relatos_asegurado", "relatos_conductor", "inspecciones", "testigos"]:
                item_data = self._process_image_data(item_data)

            item_data["siniestro_id"] = siniestro.id
            db_item = model_class(**item_data)
            self.db.add(db_item)

        self.db.commit()
        return {"message": f"Sección '{section}' actualizada", "siniestro_id": siniestro.id}

    def _update_json_section(self, siniestro: models.Siniestro, section: str, data: Any) -> Dict[str, Any]:
        """Update JSON-type sections"""
        import json
        setattr(siniestro, section, json.dumps(data))
        self.db.commit()
        return {"message": f"Sección '{section}' actualizada", "siniestro_id": siniestro.id}

    def _process_image_data(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process image data for relatos and inspecciones"""
        imagen_url = item_data.get("imagen_url")
        if imagen_url and imagen_url.strip():
            try:
                image_data = download_image_from_url(imagen_url)
                if image_data:
                    import base64
                    item_data["imagen_base64"] = base64.b64encode(image_data).decode("utf-8")
                    item_data["imagen_content_type"] = "image/jpeg"
            except Exception as e:
                logger.warning(f"No se pudo procesar imagen: {e}")

        return item_data

    def create_testigo(self, siniestro_id: int, testigo_data: schemas.TestigoCreate) -> models.Testigo:
        """Create a new testigo"""
        siniestro = self.get_siniestro(siniestro_id)
        if not siniestro:
            raise ValueError(f"Siniestro {siniestro_id} no encontrado")

        # Calculate next numero_relato
        max_num = self.db.query(models.Testigo).filter(
            models.Testigo.siniestro_id == siniestro_id
        ).count()
        numero_relato = max_num + 1

        db_testigo = models.Testigo(
            siniestro_id=siniestro_id,
            numero_relato=numero_relato,
            **testigo_data.model_dump()
        )
        self.db.add(db_testigo)
        self.db.commit()
        self.db.refresh(db_testigo)
        return db_testigo
