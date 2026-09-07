import os
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "backend" / "horizon_academy.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mensaje_usuario = Column(Text, nullable=False)
    respuesta_bot = Column(Text, nullable=False)
    escalado = Column(Boolean, default=False)
    tokens_usados = Column(Integer, default=0)
    costo_estimado = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    escalamientos = relationship("SolicitudEscalamiento", back_populates="consulta")

class SolicitudEscalamiento(Base):
    __tablename__ = "solicitudes_escalamiento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id"), nullable=True)
    nombre_contacto = Column(String(255), nullable=False)
    correo_contacto = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=True)
    estado = Column(String(50), default="Pendiente")
    created_at = Column(DateTime, default=datetime.utcnow)

    consulta = relationship("Consulta", back_populates="escalamientos")

class DocumentoRAG(Base):
    __tablename__ = "documentos_rag"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_archivo = Column(String(255), nullable=False)
    total_chunks = Column(Integer, nullable=False)
    fecha_ingesta = Column(DateTime, default=datetime.utcnow)

class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_contacto = Column(String(255), nullable=False)
    correo_contacto = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=False)
    curso_interes = Column(String(100), nullable=False)
    nivel = Column(String(50), nullable=True)
    modalidad = Column(String(50), nullable=True)
    franja_horaria = Column(String(50), nullable=True)
    estado = Column(String(50), default="Pendiente")
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DB_PATH}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_consulta(mensaje_usuario: str, respuesta_bot: str, escalado: bool = False, tokens_usados: int = 0, costo_estimado: float = 0.0) -> int:
    db = SessionLocal()
    try:
        consulta = Consulta(
            mensaje_usuario=mensaje_usuario,
            respuesta_bot=respuesta_bot,
            escalado=escalado,
            tokens_usados=tokens_usados,
            costo_estimado=costo_estimado
        )
        db.add(consulta)
        db.commit()
        db.refresh(consulta)
        return consulta.id
    except Exception as e:
        db.rollback()
        print(f"Error logging consulta: {e}")
        return 0
    finally:
        db.close()

def log_escalamiento(nombre_contacto: str, correo_contacto: str, telefono: str = None, consulta_id: int = None, estado: str = "Pendiente") -> int:
    db = SessionLocal()
    try:
        escalamiento = SolicitudEscalamiento(
            consulta_id=consulta_id,
            nombre_contacto=nombre_contacto,
            correo_contacto=correo_contacto,
            telefono=telefono,
            estado=estado
        )
        db.add(escalamiento)
        db.commit()
        db.refresh(escalamiento)
        return escalamiento.id
    except Exception as e:
        db.rollback()
        print(f"Error logging escalamiento: {e}")
        return 0
    finally:
        db.close()

def log_documento_rag(nombre_archivo: str, total_chunks: int) -> int:
    db = SessionLocal()
    try:
        doc = DocumentoRAG(
            nombre_archivo=nombre_archivo,
            total_chunks=total_chunks
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc.id
    except Exception as e:
        db.rollback()
        print(f"Error logging documento RAG: {e}")
        return 0
    finally:
        db.close()

def log_inscripcion(nombre_contacto: str, correo_contacto: str, telefono: str, curso_interes: str, nivel: str = "A1", modalidad: str = "Virtual", franja_horaria: str = "Mañana", estado: str = "Pendiente") -> int:
    db = SessionLocal()
    try:
        inscripcion = Inscripcion(
            nombre_contacto=nombre_contacto,
            correo_contacto=correo_contacto,
            telefono=telefono,
            curso_interes=curso_interes,
            nivel=nivel,
            modalidad=modalidad,
            franja_horaria=franja_horaria,
            estado=estado
        )
        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion.id
    except Exception as e:
        db.rollback()
        print(f"Error logging inscripcion: {e}")
        return 0
    finally:
        db.close()

def get_all_inscriptions():
    db = SessionLocal()
    try:
        return db.query(Inscripcion).all()
    finally:
        db.close()

