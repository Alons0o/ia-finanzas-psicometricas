from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# Intentamos la importación estándar de tu proyecto
try:
    from app.db.session import Base
except ImportError:
    # Si por alguna razón falla, buscamos una ruta alternativa
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from app.db.session import Base

class Movimiento(Base):
    __tablename__ = "movimientos"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)
    descripcion = Column(String(255), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    satisfaccion = relationship("MetricaSatisfaccion", back_populates="movimiento", uselist=False)