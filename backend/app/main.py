from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import siniestros

app = FastAPI(
    title="Sistema de Informes de Siniestros API",
    description="API para gestión de informes de siniestros vehiculares",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(siniestros.router, prefix="/api/v1", tags=["siniestros"])

@app.get("/")
async def root():
    return {"message": "API de Sistema de Informes de Siniestros"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
