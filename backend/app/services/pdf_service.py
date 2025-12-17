"""
PDF Service - PDF Generation Layer

Handles all PDF generation logic, separating it from business logic and HTTP handling.
"""

from typing import Optional, Dict, Any
from fastapi.responses import Response
from sqlalchemy.orm import Session, selectinload
from .. import models
from ..utils.pdf_generator import generate_pdf, generate_unsigned_pdf
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """Service for PDF generation operations"""

    def __init__(self, db: Session):
        self.db = db

    def generate_siniestro_pdf(
        self, siniestro_id: int, sign_document: bool = True
    ) -> Response:
        """Generate PDF for a siniestro"""
        siniestro = self._get_siniestro_with_relations(siniestro_id)
        if not siniestro:
            raise ValueError(f"Siniestro {siniestro_id} no encontrado")

        try:
            pdf_data = generate_pdf(siniestro, sign_document)
            filename = self._generate_filename(siniestro, sign_document)

            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                    "Content-Length": str(len(pdf_data)),
                },
            )
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            raise

    def generate_unsigned_pdf(self, siniestro_id: int) -> Response:
        """Generate unsigned PDF for testing"""
        siniestro = self._get_siniestro_with_relations(siniestro_id)
        if not siniestro:
            raise ValueError(f"Siniestro {siniestro_id} no encontrado")

        try:
            pdf_data = generate_unsigned_pdf(siniestro)
            filename = self._generate_filename(siniestro, False)

            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                    "Content-Length": str(len(pdf_data)),
                },
            )
        except Exception as e:
            logger.error(f"Error generando PDF sin firma: {e}")
            raise

    def generate_diagnostic_pdf(self) -> Response:
        """Generate diagnostic PDF"""
        try:
            from ..utils.pdf_generator import generate_diagnostic_pdf
            pdf_bytes = generate_diagnostic_pdf(self.db)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=diagnostico.pdf"}
            )
        except Exception as e:
            logger.error(f"Error generando PDF diagnóstico: {e}")
            raise

    def generate_test_pdf(self) -> Response:
        """Generate test PDF"""
        try:
            from ..utils.pdf_generator import generate_test_pdf
            pdf_bytes = generate_test_pdf()
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=test.pdf"}
            )
        except Exception as e:
            logger.error(f"Error generando PDF de prueba: {e}")
            raise

    def _get_siniestro_with_relations(
        self, siniestro_id: int
    ) -> Optional[models.Siniestro]:
        """Get siniestro with all necessary relations loaded"""
        return (
            self.db.query(models.Siniestro)
            .options(
                selectinload(models.Siniestro.asegurado),
                selectinload(models.Siniestro.beneficiario),
                selectinload(models.Siniestro.conductor),
                selectinload(models.Siniestro.objeto_asegurado),
                selectinload(models.Siniestro.antecedentes),
                selectinload(models.Siniestro.relatos_asegurado),
                selectinload(models.Siniestro.relatos_conductor),
                selectinload(models.Siniestro.inspecciones),
                selectinload(models.Siniestro.testigos),
                selectinload(models.Siniestro.visita_taller),
            )
            .filter(models.Siniestro.id == siniestro_id)
            .first()
        )

    def _generate_filename(self, siniestro: models.Siniestro, signed: bool) -> str:
        """Generate appropriate filename for PDF"""
        import unicodedata
        import re

        reclamo = siniestro.reclamo_num or str(siniestro.id)
        filename_base = (
            unicodedata.normalize("NFKD", reclamo)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )
        filename_base = re.sub(r"[^\w\-_\.]", "_", filename_base)

        if signed:
            return f"{filename_base}.pdf"
        else:
            return f"{filename_base}_sin_firma.pdf"
