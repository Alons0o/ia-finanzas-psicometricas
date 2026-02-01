from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class MetricaSatisfaccion(Base): # <--- Revisa que esté escrito así
    __tablename__ = "metricas_satisfaccion"

    id = Column(Integer, primary_key=True, index=True)
    movimiento_id = Column(Integer, ForeignKey("movimientos.id"), unique=True)
    
    nivel = Column(Integer, nullable=False)  # Escala 1-10
    comentario = Column(String(500), nullable=True)

    # Relación inversa hacia el modelo Movimiento
    movimiento = relationship("Movimiento", back_populates="satisfaccion")