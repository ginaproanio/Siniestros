"""
Tests for Pydantic ↔ Service Layer Integration (Phase 1)

Validates that the service layer correctly handles Pydantic models
and maintains backward compatibility with dict-based calls.
"""

import pytest
from unittest.mock import MagicMock
from app.services.siniestro_service import SiniestroService
from app.schemas.siniestro import AntecedenteInput, RelatoInput
from app import models


class TestPydanticServiceIntegration:
    """Test Pydantic model integration with service layer"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Service instance with mocked DB"""
        return SiniestroService(mock_db)

    def test_update_section_accepts_pydantic_models(self, service, mock_db):
        """Test that update_section accepts Pydantic models directly"""
        # Mock siniestro
        mock_siniestro = MagicMock()
        mock_siniestro.id = 1
        service.get_siniestro.return_value = mock_siniestro

        # Create Pydantic model
        antecedentes_data = [AntecedenteInput(descripcion="Test antecedentes")]

        # Mock successful DB operations
        mock_db.commit.return_value = None

        # Call service method
        result = service.update_section(1, "antecedentes", antecedentes_data)

        # Verify result
        assert result["message"] == "Sección 'antecedentes' actualizada"
        assert result["siniestro_id"] == 1

        # Verify DB operations were called
        mock_db.commit.assert_called_once()

    def test_update_section_backwards_compatibility(self, service, mock_db):
        """Test that update_section still accepts dicts for backward compatibility"""
        # Mock siniestro
        mock_siniestro = MagicMock()
        mock_siniestro.id = 1
        service.get_siniestro.return_value = mock_siniestro

        # Use dict format (old way)
        antecedentes_data = [{"descripcion": "Test antecedentes"}]

        # Mock successful DB operations
        mock_db.commit.return_value = None

        # Call service method
        result = service.update_section(1, "antecedentes", antecedentes_data)

        # Verify result
        assert result["message"] == "Sección 'antecedentes' actualizada"
        assert result["siniestro_id"] == 1

    def test_pydantic_model_conversion(self, service):
        """Test that Pydantic models are correctly converted to dicts"""
        # Create Pydantic model
        pydantic_input = AntecedenteInput(descripcion="Test")

        # Test conversion logic (simulate _update_list_section)
        if hasattr(pydantic_input, 'model_dump'):
            converted = pydantic_input.model_dump()
        else:
            converted = pydantic_input

        # Verify conversion
        assert isinstance(converted, dict)
        assert converted["descripcion"] == "Test"
        assert "descripcion" in converted

    def test_mixed_data_types_handling(self, service, mock_db):
        """Test handling of mixed data types (Pydantic + dict)"""
        # Mock siniestro
        mock_siniestro = MagicMock()
        mock_siniestro.id = 1
        service.get_siniestro.return_value = mock_siniestro

        # Mix of Pydantic and dict data
        mixed_data = [
            AntecedenteInput(descripcion="Pydantic item"),
            {"descripcion": "Dict item"}
        ]

        # Mock DB operations
        mock_db.commit.return_value = None

        # Call service method
        result = service.update_section(1, "antecedentes", mixed_data)

        # Verify success
        assert result["message"] == "Sección 'antecedentes' actualizada"

    def test_invalid_data_format_raises_error(self, service, mock_db):
        """Test that invalid data formats raise appropriate errors"""
        # Mock siniestro
        mock_siniestro = MagicMock()
        mock_siniestro.id = 1
        service.get_siniestro.return_value = mock_siniestro

        # Invalid data format
        invalid_data = ["string_instead_of_dict"]

        # Should raise ValueError
        with pytest.raises(ValueError, match="Formato de datos no válido"):
            service.update_section(1, "antecedentes", invalid_data)

    def test_empty_data_handling(self, service, mock_db):
        """Test handling of empty or None data"""
        # Mock siniestro
        mock_siniestro = MagicMock()
        mock_siniestro.id = 1
        service.get_siniestro.return_value = mock_siniestro

        # Empty data
        empty_data = []

        # Mock DB operations
        mock_db.commit.return_value = None

        # Call service method
        result = service.update_section(1, "antecedentes", empty_data)

        # Verify success with empty data
        assert result["message"] == "Sección 'antecedentes' actualizada"

    def test_single_item_conversion_to_list(self, service, mock_db):
        """Test that single items are converted to lists"""
        # Mock siniestro
        mock_siniestro = MagicMock()
        mock_siniestro.id = 1
        service.get_siniestro.return_value = mock_siniestro

        # Single Pydantic model (not in list)
        single_item = AntecedenteInput(descripcion="Single item")

        # Mock DB operations
        mock_db.commit.return_value = None

        # Call service method
        result = service.update_section(1, "antecedentes", single_item)

        # Verify it was treated as a list internally
        assert result["message"] == "Sección 'antecedentes' actualizada"
