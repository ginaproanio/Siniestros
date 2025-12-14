from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Siniestro(Base):
    __tablename__ = "siniestros"

    id = Column(Integer, primary_key=True, index=True)
    compania_seguros = Column(String(255), nullable=False)
    reclamo_num = Column(String(100), unique=True, nullable=False)
    fecha_siniestro = Column(DateTime(timezone=True), nullable=False)
    direccion_siniestro = Column(String(500), nullable=False)
    ubicacion_geo_lat = Column(Float)
    ubicacion_geo_lng = Column(Float)
    danos_terceros = Column(Boolean, default=False)
    ejecutivo_cargo = Column(String(255))
    fecha_designacion = Column(DateTime(timezone=True))
    tipo_siniestro = Column(String(100), default="Vehicular")
    fecha_reportado = Column(DateTime(timezone=True))  # Fecha cuando se reportó el siniestro
    cobertura = Column(String(100))  # Tipo de cobertura (Todo riesgo, etc.)
    pdf_firmado_url = Column(String(500))  # URL del PDF firmado digitalmente
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    asegurado = relationship("Asegurado", back_populates="siniestro", uselist=False, cascade="all, delete-orphan")
    beneficiario = relationship("Beneficiario", back_populates="siniestro", uselist=False, cascade="all, delete-orphan")
    conductor = relationship("Conductor", back_populates="siniestro", uselist=False, cascade="all, delete-orphan")
    objeto_asegurado = relationship("ObjetoAsegurado", back_populates="siniestro", uselist=False, cascade="all, delete-orphan")
    visita_taller = relationship("VisitaTaller", back_populates="siniestro", uselist=False, cascade="all, delete-orphan")
    dinamica_accidente = relationship("DinamicaAccidente", back_populates="siniestro", uselist=False, cascade="all, delete-orphan")
    antecedentes = relationship("Antecedente", back_populates="siniestro")
    relatos_asegurado = relationship("RelatoAsegurado", back_populates="siniestro")
    inspecciones = relationship("Inspeccion", back_populates="siniestro")
    testigos = relationship("Testigo", back_populates="siniestro")

class Asegurado(Base):
    __tablename__ = "asegurados"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"), unique=True)
    tipo = Column(String(50))  # Natural o Jurídica
    cedula = Column(String(20))
    nombre = Column(String(255))
    celular = Column(String(20))
    direccion = Column(String(500))
    parentesco = Column(String(100))
    correo = Column(String(255))  # Correo electrónico del asegurado
    # Para persona jurídica
    ruc = Column(String(20))
    empresa = Column(String(255))
    representante_legal = Column(String(255))
    telefono = Column(String(20))

    siniestro = relationship("Siniestro", back_populates="asegurado")

class Beneficiario(Base):
    __tablename__ = "beneficiarios"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"), unique=True)
    razon_social = Column(String(255))  # Razón social del beneficiario
    cedula_ruc = Column(String(20))  # Cédula o RUC del beneficiario
    domicilio = Column(String(500))  # Domicilio del beneficiario

    siniestro = relationship("Siniestro", back_populates="beneficiario")

class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"), unique=True)
    nombre = Column(String(255), nullable=False)
    cedula = Column(String(20), nullable=False)
    celular = Column(String(20))
    direccion = Column(String(500))
    parentesco = Column(String(100))

    siniestro = relationship("Siniestro", back_populates="conductor")

class ObjetoAsegurado(Base):
    __tablename__ = "objetos_asegurados"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"), unique=True)
    placa = Column(String(20), nullable=False)
    marca = Column(String(100))
    modelo = Column(String(100))
    tipo = Column(String(50))  # Tipo de vehículo (Jeep, etc.)
    color = Column(String(50))
    ano = Column(Integer)
    serie_motor = Column(String(100))
    chasis = Column(String(100))

    siniestro = relationship("Siniestro", back_populates="objeto_asegurado")

class Antecedente(Base):
    __tablename__ = "antecedentes"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"))
    descripcion = Column(Text, nullable=False)

    siniestro = relationship("Siniestro", back_populates="antecedentes")

class RelatoAsegurado(Base):
    __tablename__ = "relatos_asegurado"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"))
    numero_relato = Column(Integer, nullable=False)
    texto = Column(Text, nullable=False)
    imagen_url = Column(String(500))  # URL de la imagen subida

    siniestro = relationship("Siniestro", back_populates="relatos_asegurado")

class Inspeccion(Base):
    __tablename__ = "inspecciones"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"))
    numero_inspeccion = Column(Integer, nullable=False)
    descripcion = Column(Text, nullable=False)
    imagen_url = Column(String(500))

    siniestro = relationship("Siniestro", back_populates="inspecciones")

class Testigo(Base):
    __tablename__ = "testigos"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"))
    numero_relato = Column(Integer, nullable=False)
    texto = Column(Text, nullable=False)
    imagen_url = Column(String(500))

    siniestro = relationship("Siniestro", back_populates="testigos")

class VisitaTaller(Base):
    __tablename__ = "visitas_taller"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"), unique=True)
    descripcion = Column(Text, nullable=False)

    siniestro = relationship("Siniestro", back_populates="visita_taller")

class DinamicaAccidente(Base):
    __tablename__ = "dinamicas_accidente"

    id = Column(Integer, primary_key=True, index=True)
    siniestro_id = Column(Integer, ForeignKey("siniestros.id"), unique=True)
    descripcion = Column(Text, nullable=False)

    siniestro = relationship("Siniestro", back_populates="dinamica_accidente")
