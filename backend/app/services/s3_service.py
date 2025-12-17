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


async def upload_file_to_s3(file: UploadFile, content: bytes = None) -> dict:
    """
    Sube archivo a S3 en DOS VERSIONES según arquitectura definida:
    1. ORIGINAL (5-10MB) - Para backup legal
    2. OPTIMIZADA (300KB) - Para PDFs y web (esta va a PostgreSQL)

    Args:
        file: Archivo UploadFile de FastAPI
        content: Contenido del archivo (opcional, si ya fue leído)

    Returns:
        dict: {
            "url_optimizada": str,  # ← Esta va a PostgreSQL (imagen_url)
            "url_original": str,    # Para backup/trazabilidad
            "content_type": str     # Tipo MIME
        }

    Raises:
        HTTPException: Si hay errores de validación o subida
    """
    import base64
    from PIL import Image
    import io

    try:
        # Validar archivo y obtener contenido si no se proporcionó
        if content is None:
            content = await validate_file(file)
        logger.info(f"Archivo validado: {file.filename}, tamaño: {len(content)} bytes")

        # Generar ID único para ambas versiones
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'

        # === VERSIÓN ORIGINAL (Backup Legal) ===
        s3_key_original = f"originales/{file_id}.{file_extension}"

        # Subir original a S3
        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key_original,
            Body=content,
            ContentType=file.content_type,
            ACL='private'
        )
        logger.info(f"Original subido: s3://{S3_BUCKET_NAME}/{s3_key_original}")

        # === VERSIÓN OPTIMIZADA (Para PostgreSQL) ===
        # Optimizar imagen para web/PDF
        try:
            # Abrir imagen con PIL
            img = Image.open(io.BytesIO(content))

            # Convertir a RGB si es necesario (para JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Redimensionar manteniendo proporción (máximo 1200px de ancho)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Optimizar calidad
            output_buffer = io.BytesIO()
            img.save(output_buffer, format='JPEG', quality=85, optimize=True)
            optimized_content = output_buffer.getvalue()

            logger.info(f"Imagen optimizada: {len(content)} → {len(optimized_content)} bytes")

        except Exception as e:
            logger.warning(f"No se pudo optimizar imagen, usando original: {e}")
            optimized_content = content

        # Subir versión optimizada
        s3_key_optimizada = f"optimizadas/{file_id}.{file_extension}"
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key_optimizada,
            Body=optimized_content,
            ContentType='image/jpeg',  # Siempre JPEG para consistencia
            ACL='private'
        )
        logger.info(f"Optimizada subida: s3://{S3_BUCKET_NAME}/{s3_key_optimizada}")

        # === GENERAR URLs ===
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')

        # URL optimizada (esta va a PostgreSQL)
        url_optimizada = f"https://{S3_BUCKET_NAME}.s3.{region}.amazonaws.com/{s3_key_optimizada}"

        # URL original (para trazabilidad/backup)
        url_original = f"https://{S3_BUCKET_NAME}.s3.{region}.amazonaws.com/{s3_key_original}"

        logger.info(f"URLs generadas - Optimizada: {url_optimizada}")

        return {
            "url_optimizada": url_optimizada,  # ← Esta va a imagen_url en PostgreSQL
            "url_original": url_original,      # Para backup legal
            "content_type": 'image/jpeg'       # Siempre JPEG optimizado
        }

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


def download_image_from_url(image_url: str) -> bytes:
    """
    Descarga imagen desde URL y retorna bytes

    Args:
        image_url: URL de la imagen a descargar

    Returns:
        bytes: Contenido de la imagen

    Raises:
        HTTPException: Si hay errores de descarga o formato
    """
    import requests
    from urllib.parse import urlparse

    try:
        # Validar URL básica
        if not image_url or not image_url.strip():
            raise HTTPException(status_code=400, detail="URL de imagen requerida")

        # Parsear URL para validación básica
        parsed_url = urlparse(image_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="URL inválida")

        logger.info(f"Descargando imagen desde: {image_url}")

        # Descargar imagen
        response = requests.get(image_url, timeout=30, stream=True)

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Error descargando imagen: HTTP {response.status_code}"
            )

        # Validar tipo de contenido
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de contenido no válido: {content_type}"
            )

        # Leer contenido
        content = response.content

        # Validar tamaño (máximo 10MB para imágenes)
        max_size = 10 * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Imagen demasiado grande. Máximo: {max_size/1024/1024}MB"
            )

        # Validar que sea realmente una imagen
        try:
            from PIL import Image
            import io
            Image.open(io.BytesIO(content)).verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Archivo no es una imagen válida")

        logger.info(f"Imagen descargada exitosamente: {len(content)} bytes")
        return content

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red descargando imagen: {e}")
        raise HTTPException(status_code=400, detail=f"Error descargando imagen: {str(e)}")
    except Exception as e:
        logger.error(f"Error procesando imagen: {e}")
        raise HTTPException(status_code=500, detail="Error procesando imagen descargada")
