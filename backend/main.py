from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn
import os
from pathlib import Path

from backend.rag import chat_engine
from backend.services import metrics_service
from backend.database import init_db, log_inscripcion, log_escalamiento, get_all_inscriptions

app = FastAPI(title="Horizon Academy AI Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Initializing Horizon Academy server & database...")
    try:
        init_db()
        chat_engine.load_documents()
    except Exception as e:
        print(f"Failed to initialize server or load documents: {e}")

class ChatRequest(BaseModel):
    message: str

class InscriptionRequest(BaseModel):
    nombre: str
    correo: str
    telefono: str
    curso: str
    nivel: Optional[str] = "A1"
    modalidad: Optional[str] = "Virtual en Vivo"
    franja_horaria: Optional[str] = "Noche"

class EscalateRequest(BaseModel):
    nombre: str
    correo: str
    telefono: Optional[str] = None
    consulta_id: Optional[int] = None

@app.post("/api/chat")
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    reply = chat_engine.ask(req.message)
    return {"reply": reply}

@app.post("/api/inscriptions")
@app.post("/inscriptions")
async def inscription_endpoint(req: InscriptionRequest):
    if not req.nombre or not req.correo or not req.telefono or not req.curso:
        raise HTTPException(status_code=400, detail="Nombre, correo, teléfono y curso son requeridos.")
    
    inscription_id = log_inscripcion(
        nombre_contacto=req.nombre,
        correo_contacto=req.correo,
        telefono=req.telefono,
        curso_interes=req.curso,
        nivel=req.nivel,
        modalidad=req.modalidad,
        franja_horaria=req.franja_horaria
    )
    
    if inscription_id > 0:
        return {
            "status": "success",
            "message": "Inscripción registrada exitosamente.",
            "inscription_id": inscription_id
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo guardar la inscripción en la base de datos.")

@app.get("/api/inscriptions")
@app.get("/inscriptions")
async def get_inscriptions_endpoint():
    inscriptions = get_all_inscriptions()
    return [
        {
            "id": ins.id,
            "nombre": ins.nombre_contacto,
            "correo": ins.correo_contacto,
            "telefono": ins.telefono,
            "curso": ins.curso_interes,
            "nivel": ins.nivel,
            "modalidad": ins.modalidad,
            "franja_horaria": ins.franja_horaria,
            "estado": ins.estado,
            "created_at": ins.created_at.isoformat() if ins.created_at else None
        }
        for ins in inscriptions
    ]

@app.post("/api/escalate")
@app.post("/escalate")
async def escalate_endpoint(req: EscalateRequest):
    if not req.nombre or not req.correo:
        raise HTTPException(status_code=400, detail="Nombre y correo son requeridos")
        
    escalate_id = log_escalamiento(
        nombre_contacto=req.nombre,
        correo_contacto=req.correo,
        telefono=req.telefono,
        consulta_id=req.consulta_id
    )
    return {"status": "success", "escalate_id": escalate_id}

@app.get("/api/metrics")
@app.get("/metrics")
async def metrics_endpoint():
    return metrics_service.get_metrics()

@app.post("/api/metrics/reset")
@app.post("/metrics/reset")
async def reset_metrics_endpoint():
    metrics_service.reset()
    return {"status": "success", "message": "Metrics reset successfully"}

@app.get("/api/config")
@app.get("/config")
async def config_endpoint():
    return {
        "escalation_form_url": os.getenv("ESCALATION_FORM_URL", "https://docs.google.com/forms/d/e/1FAIpQLSdAyhhqdotfhe9bwKaCC0faNaArmJLSjQOmuD9feRl0pEd95A/viewform")
    }

# Serve static frontend (if built)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("/")
    def root_fallback():
        return {"message": "Backend API is running. Frontend build not found."}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=3000, reload=True)
