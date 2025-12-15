from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Base schemas
class SiniestroBase(BaseModel):
    compania_seguros: str = Field(..., max_length=255)
    ruc_compania: Optional[str] = Field(None, max_length=20)
    tipo_reclamo: Optional[str] = Field(None, max_length=50)
    poliza: Optional[str] = Field(None, max_length=50)
    reclamo_num: str = Field(..., max_length=100)
    fecha_siniestro: datetime
    fecha_reportado: Optional[datetime] = None
    direccion_siniestro: str = Field(..., max_length=500)
    ubicacion_geo_lat: Optional[float] = None
    ubicacion_geo_lng: Optional[float] = None
    danos_terceros: bool = False
    ejecutivo_cargo: Optional[str] = Field(None, max_length=255)
    fecha_designacion: Optional[datetime] = None
    tipo_siniestro: str = Field("Vehicular", max_length=100)
    cobertura: Optional[str] = Field(None, max_length=100)
    pdf_firmado_url: Optional[str] = Field(None, max_length=500)

    # Nuevos campos para declaración del siniestro
    fecha_declaracion: Optional[datetime] = None
    persona_declara_tipo: Optional[str] = Field(None, max_length=20)
    persona_declara_cedula: Optional[str] = Field(None, max_length=20)
    persona_declara_nombre: Optional[str] = Field(None, max_length=255)
    persona_declara_relacion: Optional[str] = Field(None, max_length=255)

    # Misiva de investigación (no se muestra en PDF)
    misiva_investigacion: Optional[str] = None

class AseguradoBase(BaseModel):
    tipo: str = Field(..., max_length=50)
    cedula: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=255)
    celular: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=255)
    direccion: Optional[str] = Field(None, max_length=500)
    parentesco: Optional[str] = Field(None, max_length=100)
    ruc: Optional[str] = Field(None, max_length=20)
    empresa: Optional[str] = Field(None, max_length=255)
    representante_legal: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=20)

class ConductorBase(BaseModel):
    nombre: str = Field(..., max_length=255)
    cedula: str = Field(..., max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=500)
    parentesco: Optional[str] = Field(None, max_length=100)

class ObjetoAseguradoBase(BaseModel):
    placa: str = Field(..., max_length=20)
    marca: Optional[str] = Field(None, max_length=100)
    modelo: Optional[str] = Field(None, max_length=100)
    tipo: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=50)
    ano: Optional[int] = None
    serie_motor: Optional[str] = Field(None, max_length=100)
    chasis: Optional[str] = Field(None, max_length=100)

class BeneficiarioBase(BaseModel):
    razon_social: Optional[str] = Field(None, max_length=255)
    cedula_ruc: Optional[str] = Field(None, max_length=20)
    domicilio: Optional[str] = Field(None, max_length=500)

class RelatoBase(BaseModel):
    numero_relato: int
    texto: str
    imagen_url: Optional[str] = Field(None, max_length=500)

class InspeccionBase(BaseModel):
    numero_inspeccion: int
    descripcion: str
    imagen_url: Optional[str] = Field(None, max_length=500)

# Create schemas
class SiniestroCreate(SiniestroBase):
    pass

class AseguradoCreate(AseguradoBase):
    pass

class ConductorCreate(ConductorBase):
    pass

class ObjetoAseguradoCreate(ObjetoAseguradoBase):
    pass

class BeneficiarioCreate(BeneficiarioBase):
    pass

class RelatoAseguradoCreate(RelatoBase):
    pass

class InspeccionCreate(InspeccionBase):
    pass

class TestigoCreate(RelatoBase):
    pass

class AntecedenteCreate(BaseModel):
    descripcion: str

class VisitaTallerCreate(BaseModel):
    descripcion: str

class DinamicaAccidenteCreate(BaseModel):
    descripcion: str

# Response schemas
class SiniestroResponse(SiniestroBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AseguradoResponse(AseguradoBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class ConductorResponse(ConductorBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class ObjetoAseguradoResponse(ObjetoAseguradoBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class BeneficiarioResponse(BeneficiarioBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class RelatoAseguradoResponse(RelatoBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class InspeccionResponse(InspeccionBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class TestigoResponse(RelatoBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class RelatoConductorResponse(RelatoBase):
    id: int
    siniestro_id: int

    class Config:
        from_attributes = True

class AntecedenteResponse(BaseModel):
    id: int
    siniestro_id: int
    descripcion: str

    class Config:
        from_attributes = True

class VisitaTallerResponse(BaseModel):
    id: int
    siniestro_id: int
    descripcion: str

    class Config:
        from_attributes = True

class DinamicaAccidenteResponse(BaseModel):
    id: int
    siniestro_id: int
    descripcion: str

    class Config:
        from_attributes = True

# Full siniestro response with all relationships
class SiniestroFullResponse(SiniestroResponse):
    asegurado: Optional[AseguradoResponse] = None
    beneficiario: Optional[BeneficiarioResponse] = None
    conductor: Optional[ConductorResponse] = None
    objeto_asegurado: Optional[ObjetoAseguradoResponse] = None
    antecedentes: List[AntecedenteResponse] = []
    relatos_asegurado: List[RelatoAseguradoResponse] = []
    relatos_conductor: List[RelatoConductorResponse] = []
    inspecciones: List[InspeccionResponse] = []
    testigos: List[TestigoResponse] = []
    visita_taller: Optional[VisitaTallerResponse] = None
    dinamica_accidente: Optional[DinamicaAccidenteResponse] = None

# Update schemas
class SiniestroUpdate(BaseModel):
    compania_seguros: Optional[str] = None
    ruc_compania: Optional[str] = None
    tipo_reclamo: Optional[str] = None
    poliza: Optional[str] = None
    reclamo_num: Optional[str] = None
    fecha_siniestro: Optional[datetime] = None
    fecha_reportado: Optional[datetime] = None
    direccion_siniestro: Optional[str] = None
    ubicacion_geo_lat: Optional[float] = None
    ubicacion_geo_lng: Optional[float] = None
    danos_terceros: Optional[bool] = None
    ejecutivo_cargo: Optional[str] = None
    fecha_designacion: Optional[datetime] = None
    tipo_siniestro: Optional[str] = None
    cobertura: Optional[str] = None
    pdf_firmado_url: Optional[str] = None

    # Nuevos campos para declaración del siniestro
    fecha_declaracion: Optional[datetime] = None
    persona_declara_tipo: Optional[str] = None
    persona_declara_cedula: Optional[str] = None
    persona_declara_nombre: Optional[str] = None
    persona_declara_relacion: Optional[str] = None

    # Misiva de investigación
    misiva_investigacion: Optional[str] = None

    # Campos de investigación recabada
    evidencias_complementarias: Optional[str] = None
    evidencias_complementarias_imagen_url: Optional[str] = None
    otras_diligencias: Optional[str] = None
    otras_diligencias_imagen_url: Optional[str] = None
    visita_taller_descripcion: Optional[str] = None
    visita_taller_imagen_url: Optional[str] = None
    observaciones: Optional[List[str]] = None
    recomendacion_pago_cobertura: Optional[List[str]] = None
    conclusiones: Optional[List[str]] = None
    anexo: Optional[List[str]] = None

    # Arrays de investigación que vienen del frontend
    antecedentes: Optional[List[AntecedenteCreate]] = None
    relatos_asegurado: Optional[List[RelatoAseguradoCreate]] = None
    relatos_conductor: Optional[List[RelatoBase]] = None  # Usando RelatoBase ya que es similar
    inspecciones: Optional[List[InspeccionCreate]] = None
    testigos: Optional[List[TestigoCreate]] = None

    # Relaciones anidadas para actualización
    objeto_asegurado: Optional[ObjetoAseguradoCreate] = None
    asegurado: Optional[AseguradoCreate] = None
    beneficiario: Optional[BeneficiarioCreate] = None
    conductor: Optional[ConductorCreate] = None
