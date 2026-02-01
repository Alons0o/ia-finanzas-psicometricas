from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.session import Base

class MetaAhorro(Base):
    __tablename__ = "metas_ahorro"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    monto_objetivo = Column(Float, nullable=False)
    monto_actual = Column(Float, default=0.0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)