#!/usr/bin/env python3
"""
Test script para generación de PDF
"""

import sys
sys.path.append('.')

from app.database import get_db
from app.services.pdf_service import PDFService
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_generation():
    print('🧪 PRUEBA DE GENERACIÓN DE PDF')
    print('=' * 50)

    db: Session = next(get_db())

    try:
        # Crear servicio PDF
        pdf_service = PDFService(db)

        # Intentar generar PDF para el primer siniestro
        from app.models.siniestro import Siniestro
        siniestro = db.query(Siniestro).first()

        if not siniestro:
            print('❌ No hay siniestros en la base de datos')
            return

        siniestro_id = siniestro.id
        print(f'📄 Intentando generar PDF para siniestro ID: {siniestro_id}')

        # Generar PDF
        try:
            pdf_response = pdf_service.generate_siniestro_pdf(siniestro_id, sign_document=False)
            pdf_data = pdf_response.body

            if pdf_data:
                pdf_size = len(pdf_data)
                print(f'✅ PDF generado exitosamente: {pdf_size} bytes')

                # Verificar que es un PDF válido
                if pdf_data.startswith(b'%PDF-'):
                    print('✅ PDF tiene encabezado válido')
                else:
                    print('❌ PDF no tiene encabezado válido')
                    print(f'📄 Comienza con: {pdf_data[:50]}')

                # Guardar PDF para inspección
                with open('test_output.pdf', 'wb') as f:
                    f.write(pdf_data)
                print('💾 PDF guardado como test_output.pdf')

            else:
                print('❌ PDF generado es vacío')

        except Exception as e:
            print(f'❌ Error generando PDF: {e}')
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f'❌ Error general: {e}')
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == '__main__':
    test_pdf_generation()
