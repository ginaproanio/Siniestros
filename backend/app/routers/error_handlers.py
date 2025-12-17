"""
Error Handling Utilities for API Routers

Centralized error handling to eliminate code duplication across endpoints.
Provides consistent error logging and HTTP exception raising.
"""

import logging
import traceback
from typing import Any, Dict, Optional
from fastapi import HTTPException

from ..services.validation_service import ValidationService

logger = logging.getLogger(__name__)


def handle_api_error(
    error: Exception,
    operation: str,
    context: Optional[Dict[str, Any]] = None,
    validation_service: Optional[ValidationService] = None
) -> None:
    """
    Centralized error handling for API endpoints.

    Args:
        error: The exception that occurred
        operation: Description of the operation being performed
        context: Optional context information for logging
        validation_service: Optional validation service for safe error messages

    Raises:
        HTTPException: With appropriate status code and message
    """
    context = context or {}

    if isinstance(error, ValueError):
        # Validation errors - 400 Bad Request
        logger.warning(f"Validation error in {operation}: {str(error)}")
        raise HTTPException(status_code=400, detail=str(error))

    elif isinstance(error, HTTPException):
        # Re-raise HTTP exceptions as-is
        raise error

    else:
        # Unexpected errors - 500 Internal Server Error
        # Log detailed error information for debugging
        logger.error(f"Unexpected error in {operation}: {str(error)}")

        # Add context information if provided
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            logger.error(f"Context: {context_str}")

        # Log full traceback for debugging
        logger.error(f"Traceback: {traceback.format_exc()}")

        # Return safe error message
        if validation_service:
            safe_message = validation_service.create_safe_error_message(error)
        else:
            safe_message = "Error interno del servidor"

        raise HTTPException(status_code=500, detail=safe_message)


def create_error_response(
    message: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error response dictionary.

    Args:
        message: Error message
        status_code: HTTP status code
        details: Optional additional details

    Returns:
        Dict with standardized error format
    """
    response = {
        "error": message,
        "status_code": status_code,
    }

    if details:
        response["details"] = details

    return response


def get_validation_service() -> ValidationService:
    """
    Factory function to get ValidationService instance.

    Centralizes validation service instantiation to avoid code duplication.
    """
    return ValidationService()
