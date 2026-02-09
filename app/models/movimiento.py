import sys
import os
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# Esto fuerza a Python a reconocer la carpeta raíz 'PRUEBA'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from app.db.session import Base
except ModuleNotFoundError:
    # Si falla la importación absoluta, intentamos una relativa o directa
    from db.session import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    tipo = Column(String(10), nullable=False)
    
    movimientos = relationship("Movimiento", back_populates="categoria")

class Movimiento(Base):
    __tablename__ = "movimientos"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)
    descripcion = Column(String(255), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    categoria = relationship("Categoria", back_populates="movimientos")
    satisfaccion = relationship("MetricaSatisfaccion", back_populates="movimiento", uselist=False)