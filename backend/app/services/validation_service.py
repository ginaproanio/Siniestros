"""
Validation Service - Input Validation and Security Layer

Handles all input validation, sanitization, and security checks.
"""

from typing import Any, Dict, List, Optional
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for input validation and security"""

    # Maximum file sizes
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_PDF_SIZE = 50 * 1024 * 1024    # 50MB

    # Valid file extensions
    VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    VALID_DOCUMENT_EXTENSIONS = {'.pdf'}

    # URL validation patterns
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)  # path

    def validate_siniestro_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate siniestro creation/update data"""
        errors = []

        # Validate reclamo_num
        if 'reclamo_num' in data:
            if not self._is_valid_reclamo_num(data['reclamo_num']):
                errors.append("Número de reclamo inválido")

        # Validate dates
        if 'fecha_siniestro' in data:
            if not self._is_valid_date(data['fecha_siniestro']):
                errors.append("Fecha de siniestro inválida")

        if 'fecha_reportado' in data:
            if not self._is_valid_date(data['fecha_reportado']):
                errors.append("Fecha reportado inválida")

        # Validate coordinates
        if 'ubicacion_geo_lat' in data:
            if not self._is_valid_latitude(data['ubicacion_geo_lat']):
                errors.append("Latitud inválida")

        if 'ubicacion_geo_lng' in data:
            if not self._is_valid_longitude(data['ubicacion_geo_lng']):
                errors.append("Longitud inválida")

        # Validate phone numbers
        phone_fields = ['persona_declara_cedula']
        for field in phone_fields:
            if field in data and data[field]:
                if not self._is_valid_cedula(data[field]):
                    errors.append(f"{field} inválido")

        # Validate URLs
        url_fields = ['pdf_firmado_url']
        for field in url_fields:
            if field in data and data[field]:
                if not self._is_valid_url(data[field]):
                    errors.append(f"{field} URL inválida")

        if errors:
            raise ValueError(f"Datos inválidos: {', '.join(errors)}")

        return self._sanitize_data(data)

    def validate_image_url(self, url: str) -> bool:
        """Validate image URL"""
        if not url or not url.strip():
            return False

        if not self._is_valid_url(url):
            return False

        # Check for common image hosting domains
        parsed = urlparse(url.lower())
        allowed_domains = [
            'amazonaws.com', 'cloudfront.net', 'imgur.com',
            'localhost', '127.0.0.1', '0.0.0.0'
        ]

        domain_allowed = any(domain in parsed.netloc for domain in allowed_domains)
        if not domain_allowed:
            logger.warning(f"URL domain not in allowlist: {parsed.netloc}")

        return True

    def validate_file_size(self, file_size: int, file_type: str = 'image') -> bool:
        """Validate file size"""
        if file_type == 'image':
            max_size = self.MAX_IMAGE_SIZE
        elif file_type == 'pdf':
            max_size = self.MAX_PDF_SIZE
        else:
            max_size = self.MAX_IMAGE_SIZE

        return file_size <= max_size

    def validate_file_extension(self, filename: str, file_type: str = 'image') -> bool:
        """Validate file extension"""
        if not filename:
            return False

        import os
        ext = os.path.splitext(filename.lower())[1]

        if file_type == 'image':
            return ext in self.VALID_IMAGE_EXTENSIONS
        elif file_type == 'pdf':
            return ext in self.VALID_DOCUMENT_EXTENSIONS

        return False

    def validate_section_data(self, section: str, data: Any) -> Any:
        """
        Validate section-specific data.

        Note: Since Phase 1, Pydantic handles most validations.
        This service now focuses on business rules and edge cases.
        """
        # Pydantic already validated the structure, so we focus on business logic
        if section in ['asegurado', 'conductor', 'objeto_asegurado']:
            return self._validate_entity_business_rules(data, section)
        elif section in ['antecedentes', 'relatos_asegurado', 'relatos_conductor',
                        'inspecciones', 'testigos']:
            return self._validate_list_business_rules(data, section)
        elif section in ['evidencias_complementarias', 'otras_diligencias',
                        'detalles_visita_taller', 'observaciones',
                        'recomendacion_pago_cobertura', 'conclusiones', 'anexo']:
            return self._validate_json_business_rules(data, section)
        else:
            raise ValueError(f"Sección '{section}' no reconocida")

    def _validate_entity_business_rules(self, data: Any, section: str) -> Any:
        """
        Validate entity business rules (asegurado, conductor, etc.)

        Since Pydantic handles structural validation, focus on business logic.
        """
        # For Phase 2, entities are validated by Pydantic, so we just pass through
        # Future business rules can be added here (e.g., duplicate cedula checks)
        return data

    def _validate_list_business_rules(self, data: Any, section: str) -> Any:
        """
        Validate list business rules (antecedentes, relatos, inspecciones, etc.)

        Since Pydantic handles structural validation, focus on business logic.
        """
        # For Phase 2, list data is validated by Pydantic, so we just pass through
        # Future business rules can be added here (e.g., duplicate image URLs)
        return data

    def _validate_json_business_rules(self, data: Any, section: str) -> Any:
        """
        Validate JSON business rules (observaciones, conclusiones, etc.)

        Since Pydantic handles structural validation, focus on business logic.
        """
        # For Phase 2, JSON data is validated by Pydantic, so we just pass through
        # Future business rules can be added here (e.g., content analysis)
        return data

    def _validate_json_data(self, data: Any) -> Any:
        """Validate JSON data"""
        # Allow any structure for now, but ensure it's serializable
        import json
        try:
            json.dumps(data)
            return data
        except (TypeError, ValueError):
            raise ValueError("Datos no serializables a JSON")

    def _is_valid_reclamo_num(self, value: str) -> bool:
        """Validate reclamo number format"""
        if not value or not isinstance(value, str):
            return False
        # Allow alphanumeric, dashes, underscores, dots
        return bool(re.match(r'^[A-Za-z0-9\-_\.]+$', value))

    def _is_valid_date(self, value: Any) -> bool:
        """Validate date format"""
        from datetime import datetime
        try:
            if isinstance(value, str):
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif hasattr(value, 'year'):  # datetime object
                pass
            else:
                return False
            return True
        except (ValueError, AttributeError):
            return False

    def _is_valid_latitude(self, value: float) -> bool:
        """Validate latitude (-90 to 90)"""
        try:
            return -90 <= float(value) <= 90
        except (ValueError, TypeError):
            return False

    def _is_valid_longitude(self, value: float) -> bool:
        """Validate longitude (-180 to 180)"""
        try:
            return -180 <= float(value) <= 180
        except (ValueError, TypeError):
            return False

    def _is_valid_cedula(self, value: str) -> bool:
        """Validate Ecuadorian ID format"""
        if not value or not isinstance(value, str):
            return False
        # Basic validation: 10 digits or RUC format
        return bool(re.match(r'^\d{10}(\d{3})?$', value.replace('-', '').replace('.', '')))

    def _is_valid_email(self, value: str) -> bool:
        """Validate email format"""
        if not value or not isinstance(value, str):
            return False
        return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value))

    def _is_valid_phone(self, value: str) -> bool:
        """Validate phone number format"""
        if not value or not isinstance(value, str):
            return False
        # Allow digits, spaces, dashes, parentheses
        clean = re.sub(r'[\s\-\(\)]', '', value)
        return bool(re.match(r'^\+?\d{7,15}$', clean))

    def _is_valid_url(self, value: str) -> bool:
        """Validate URL format"""
        if not value or not isinstance(value, str):
            return False
        return bool(self.URL_PATTERN.match(value))

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data"""
        sanitized = {}

        for key, value in data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized[key] = re.sub(r'[<>\"\';]', '', value.strip())
            else:
                sanitized[key] = value

        return sanitized

    def create_safe_error_message(self, error: Exception) -> str:
        """Create safe error message without exposing sensitive data"""
        error_type = type(error).__name__

        # Don't expose internal details in production
        safe_messages = {
            'ValueError': 'Datos proporcionados inválidos',
            'IntegrityError': 'Error de integridad de datos',
            'OperationalError': 'Error de conexión a base de datos',
            'ProgrammingError': 'Error interno del sistema',
        }

        return safe_messages.get(error_type, 'Error interno del servidor')
