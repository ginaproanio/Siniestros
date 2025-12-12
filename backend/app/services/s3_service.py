"""
Servicio de AWS S3 para manejo de archivos de siniestros
"""
import os
import uuid
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from typing import Optional, Tuple
from pathlib import Path


class S3Service:
    """Servicio para operaciones con AWS S3"""

    def __init__(self):
        # Configurar credenciales de AWS desde variables de entorno de Railway
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'siniestros-bucket')

        print(f"🔧 Configuración S3 - Bucket: {self.bucket_name}, Region: {self.region_name}")

        # Inicializar cliente S3
        if self.aws_access_key_id and self.aws_secret_access_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
                print("✅ Cliente S3 inicializado correctamente")
            except Exception as e:
                print(f"❌ Error inicializando cliente S3: {e}")
                self.s3_client = None
        else:
            print("⚠️ Variables de entorno AWS no encontradas")
            # Fallback: intentar usar credenciales del archivo CSV para desarrollo local
            csv_path = Path(__file__).parent.parent.parent / 'siniestros-s3-user_accessKeys.csv'
            if csv_path.exists():
                try:
                    with open(csv_path, 'r') as f:
                        lines = f.readlines()
                        if len(lines) >= 2:
                            credentials = lines[1].strip().split(',')
                            if len(credentials) >= 2:
                                self.aws_access_key_id = credentials[0].strip()
                                self.aws_secret_access_key = credentials[1].strip()

                                self.s3_client = boto3.client(
                                    's3',
                                    aws_access_key_id=self.aws_access_key_id,
                                    aws_secret_access_key=self.aws_secret_access_key,
                                    region_name=self.region_name
                                )
                                print("✅ Credenciales AWS cargadas desde CSV (desarrollo local)")
                            else:
                                print("❌ Formato de credenciales CSV inválido")
                                self.s3_client = None
                        else:
                            print("❌ Archivo CSV no contiene credenciales")
                            self.s3_client = None
                except Exception as e:
                    print(f"❌ Error cargando credenciales desde CSV: {e}")
                    self.s3_client = None
            else:
                print("⚠️ No se encontraron credenciales AWS ni archivo CSV")
                self.s3_client = None

    def upload_file(self, file_content: bytes, filename: str, content_type: str = None) -> Optional[str]:
        """
        Subir archivo a S3

        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo
            content_type: Tipo MIME del archivo

        Returns:
            URL del archivo en S3 o None si falla
        """
        if not self.s3_client:
            print("❌ Cliente S3 no inicializado")
            return None

        try:
            # Generar nombre único para el archivo
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"

            # Crear estructura de carpetas por fecha (YYYY/MM/DD)
            from datetime import datetime
            now = datetime.now()
            folder_path = f"siniestros/{now.year}/{now.month:02d}/{now.day:02d}/"

            s3_key = f"{folder_path}{unique_filename}"

            # Extraer tipo MIME si no se proporciona
            if not content_type:
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif filename.lower().endswith('.png'):
                    content_type = 'image/png'
                elif filename.lower().endswith('.webp'):
                    content_type = 'image/webp'
                elif filename.lower().endswith('.pdf'):
                    content_type = 'application/pdf'
                else:
                    content_type = 'application/octet-stream'

            # Subir archivo a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'  # Hacer público para acceso directo
            )

            # Generar URL pública del archivo
            s3_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"

            print(f"✅ Archivo subido a S3: {s3_url}")
            return s3_url

        except NoCredentialsError:
            print("❌ Error de credenciales AWS")
            return None
        except PartialCredentialsError:
            print("❌ Credenciales AWS incompletas")
            return None
        except Exception as e:
            print(f"❌ Error subiendo archivo a S3: {e}")
            return None

    def download_file(self, s3_url: str) -> Optional[bytes]:
        """
        Descargar archivo desde S3

        Args:
            s3_url: URL completa del archivo en S3

        Returns:
            Contenido del archivo en bytes o None si falla
        """
        if not self.s3_client:
            print("❌ Cliente S3 no inicializado")
            return None

        try:
            # Extraer bucket y key de la URL
            # URL format: https://bucket-name.s3.region.amazonaws.com/path/to/file
            url_parts = s3_url.replace('https://', '').split('/')
            bucket = url_parts[0].split('.')[0]
            key = '/'.join(url_parts[1:])

            # Descargar archivo
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            file_content = response['Body'].read()

            print(f"✅ Archivo descargado desde S3: {len(file_content)} bytes")
            return file_content

        except Exception as e:
            print(f"❌ Error descargando archivo desde S3: {e}")
            return None

    def delete_file(self, s3_url: str) -> bool:
        """
        Eliminar archivo de S3

        Args:
            s3_url: URL completa del archivo en S3

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self.s3_client:
            print("❌ Cliente S3 no inicializado")
            return False

        try:
            # Extraer bucket y key de la URL
            url_parts = s3_url.replace('https://', '').split('/')
            bucket = url_parts[0].split('.')[0]
            key = '/'.join(url_parts[1:])

            # Eliminar archivo
            self.s3_client.delete_object(Bucket=bucket, Key=key)

            print(f"✅ Archivo eliminado de S3: {s3_url}")
            return True

        except Exception as e:
            print(f"❌ Error eliminando archivo de S3: {e}")
            return False

    def get_presigned_url(self, s3_url: str, expiration: int = 3600) -> Optional[str]:
        """
        Generar URL prefirmada para acceso temporal

        Args:
            s3_url: URL completa del archivo en S3
            expiration: Tiempo de expiración en segundos (default 1 hora)

        Returns:
            URL prefirmada o None si falla
        """
        if not self.s3_client:
            print("❌ Cliente S3 no inicializado")
            return None

        try:
            # Extraer bucket y key de la URL
            url_parts = s3_url.replace('https://', '').split('/')
            bucket = url_parts[0].split('.')[0]
            key = '/'.join(url_parts[1:])

            # Generar URL prefirmada
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket,
                    'Key': key
                },
                ExpiresIn=expiration
            )

            return presigned_url

        except Exception as e:
            print(f"❌ Error generando URL prefirmada: {e}")
            return None


# Instancia global del servicio
s3_service = S3Service()
