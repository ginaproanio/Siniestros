#!/usr/bin/env python3
"""
Script para analizar el contenido del PDF generado
"""

import sys
sys.path.append('.')

from app.database import get_db
from app.services.pdf_service import PDFService
from app.models.siniestro import Siniestro
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_pdf_content():
    print('🔍 ANÁLISIS DEL CONTENIDO DEL PDF GENERADO')
    print('=' * 60)

    db: Session = next(get_db())

    try:
        # Obtener el siniestro
        siniestro = db.query(Siniestro).first()

        if not siniestro:
            print('❌ No hay siniestros en la base de datos')
            return

        print(f'📋 SINIESTRO ID: {siniestro.id}')
        print(f'📋 RECLAMO: {siniestro.reclamo_num}')
        print(f'📋 COMPAÑÍA: {siniestro.compania_seguros}')
        print()

        # Analizar datos disponibles
        print('📊 DATOS DISPONIBLES EN EL SINIESTRO:')
        print(f'  • Información básica: ✅')
        print(f'  • Asegurado: {"✅" if siniestro.asegurado else "❌"}')
        print(f'  • Conductor: {"✅" if siniestro.conductor else "❌"}')
        print(f'  • Objeto asegurado: {"✅" if siniestro.objeto_asegurado else "❌"}')
        print(f'  • Antecedentes: {len(siniestro.antecedentes) if siniestro.antecedentes else 0}')
        print(f'  • Relatos asegurado: {len(siniestro.relatos_asegurado) if siniestro.relatos_asegurado else 0}')
        print(f'  • Relatos conductor: {len(siniestro.relatos_conductor) if siniestro.relatos_conductor else 0}')
        print(f'  • Inspecciones: {len(siniestro.inspecciones) if siniestro.inspecciones else 0}')
        print(f'  • Testigos: {len(siniestro.testigos) if siniestro.testigos else 0}')
        print()

        # Verificar si hay datos de investigación
        has_investigacion = (
            siniestro.antecedentes or siniestro.relatos_asegurado or siniestro.relatos_conductor or
            siniestro.inspecciones or siniestro.testigos or
            (siniestro.evidencias_complementarias and siniestro.evidencias_complementarias.strip()) or
            (siniestro.otras_diligencias and siniestro.otras_diligencias.strip()) or
            (siniestro.visita_taller_descripcion and siniestro.visita_taller_descripcion.strip()) or
            (siniestro.observaciones and siniestro.observaciones.strip()) or
            (siniestro.recomendacion_pago_cobertura and siniestro.recomendacion_pago_cobertura.strip()) or
            (siniestro.conclusiones and siniestro.conclusiones.strip()) or
            (siniestro.anexo and siniestro.anexo.strip())
        )

        print(f'📋 ¿TIENE DATOS DE INVESTIGACIÓN?: {"✅ SÍ" if has_investigacion else "❌ NO"}')
        print()

        # Generar PDF y analizar
        print('🧪 GENERANDO PDF PARA ANÁLISIS:')
        pdf_service = PDFService(db)

        try:
            pdf_response = pdf_service.generate_siniestro_pdf(siniestro.id, sign_document=False)
            pdf_data = pdf_response.body

            if pdf_data:
                pdf_size = len(pdf_data)
                print(f'  • Tamaño del PDF: {pdf_size} bytes')

                # Verificar si es PDF válido
                if pdf_data.startswith(b'%PDF-'):
                    print(f'  • Encabezado PDF: ✅ VÁLIDO')
                else:
                    print(f'  • Encabezado PDF: ❌ INVÁLIDO')
                    print(f'  • Comienza con: {pdf_data[:50]}')

                # Buscar texto específico en el PDF
                pdf_text = pdf_data.decode('latin-1', errors='ignore')

                # Verificar elementos clave
                elementos_pdf = [
                    ('Título principal', 'INFORME DE INVESTIGACIÓN'),
                    ('Compañía', siniestro.compania_seguros or ''),
                    ('Número reclamo', siniestro.reclamo_num or ''),
                    ('Nombre investigador', 'Susana Espinosa'),
                    ('Sección antecedentes', 'Antecedentes'),
                    ('Sección cierre', 'Sin otro particular'),
                ]

                print('  • Contenido encontrado:')
                for nombre, texto in elementos_pdf:
                    if texto and texto in pdf_text:
                        print(f'    ✅ {nombre}: encontrado')
                    else:
                        print(f'    ❌ {nombre}: NO encontrado')

                # Verificar si tiene datos de investigación
                if has_investigacion:
                    print(f'    ✅ Sección INVESTIGACIÓN: debería estar presente')
                else:
                    print(f'    ⚠️ Sección INVESTIGACIÓN: podría estar ausente (sin datos)')

                # Guardar PDF para inspección manual
                with open('pdf_analizado.pdf', 'wb') as f:
                    f.write(pdf_data)
                print(f'  • PDF guardado como: pdf_analizado.pdf')

            else:
                print('❌ PDF generado es vacío (None)')

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
    analyze_pdf_content()
