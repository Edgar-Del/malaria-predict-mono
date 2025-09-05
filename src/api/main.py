"""
API FastAPI para o Sistema de Previsão de Risco de Malária (Bié).
"""

import os
import logging
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.ingest.database_manager import DatabaseManager
from src.api.endpoints import router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Previsão de Risco de Malária (Bié)",
    description="API para previsão de risco de malária por município",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
db_manager = DatabaseManager()

# Dependências
def get_db_manager():
    return db_manager

# Incluir rotas
app.include_router(router, dependencies=[Depends(get_db_manager)])

# Eventos da aplicação
@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da aplicação."""
    logger.info("Iniciando Sistema de Previsão de Risco de Malária (Bié)")
    
    # Verificar conexão com banco
    if not db_manager.test_connection():
        logger.warning("Não foi possível conectar com o banco de dados")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento da aplicação."""
    logger.info("Encerrando Sistema de Previsão de Risco de Malária (Bié)")

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )