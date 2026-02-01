from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class MetricaSatisfaccion(Base):
    __tablename__ = "metricas_satisfaccion"
    id = Column(Integer, primary_key=True, index=True)
    movimiento_id = Column(Integer, ForeignKey("movimientos.id"))
    nivel = Column(Integer, nullable=False) # Nota: Tu IA busca .nivel, no .nivel_satisfaccion
    comentario = Column(String(255))

    movimiento = relationship("Movimiento", back_populates="satisfaccion")