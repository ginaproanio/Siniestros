"""
Servicio de AWS S3 para manejo de archivos
"""
import os
import uuid
import boto3
import logging
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'image/jpeg,image/png,image/jpg,image/webp').split(',')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'siniestrossusiespinosa')


def get_s3_client():
    """Factory para cliente S3 con validación de credenciales"""
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if not aws_access_key or not aws_secret_key:
        raise HTTPException(
            status_code=500,
            detail="Credenciales AWS S3 no configuradas"
        )

    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-2')
    )


async def validate_file(file: UploadFile) -> bytes:
    """Valida archivo y retorna contenido"""
    if not file.filename:
        raise HTTPException(400, "Nombre de archivo requerido")

    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Solo: {', '.join(ALLOWED_FILE_TYPES)}"
        )

    content = await file.read()
    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024

    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {MAX_FILE_SIZE_MB} MB"
        )

    return content


async def upload_file_to_s3(file: UploadFile) -> str:
    """
    Sube archivo a S3 y retorna URL presigned

    Args:
        file: Archivo UploadFile de FastAPI

    Returns:
        str: URL presigned válida por 7 días

    Raises:
        HTTPException: Si hay errores de validación o subida
    """
    try:
        # Validar archivo
        content = await validate_file(file)
        logger.info(f"Archivo validado: {file.filename}, tamaño: {len(content)} bytes")

        # Generar nombre único
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        s3_key = f"uploads/{unique_filename}"

        # Subir a S3
        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=content,
            ContentType=file.content_type
        )
        logger.info(f"Archivo subido a S3: s3://{S3_BUCKET_NAME}/{s3_key}")

        # Generar URL presigned
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=604800  # 7 días
        )

        return presigned_url

    except NoCredentialsError:
        logger.error("Credenciales AWS no encontradas")
        raise HTTPException(500, "Error de configuración S3")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Error S3: {error_code} - {e}")
        if error_code == 'NoSuchBucket':
            raise HTTPException(500, "Bucket S3 no existe")
        elif error_code == 'AccessDenied':
            raise HTTPException(500, "Permisos insuficientes en S3")
        else:
            raise HTTPException(500, f"Error S3: {error_code}")
    except Exception as e:
        logger.error(f"Error inesperado en upload_file_to_s3: {e}")
        raise HTTPException(500, "Error interno del servidor")
