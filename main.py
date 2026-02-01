from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal, engine, Base
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion
from app.ia.analisis_psicometrico import MotorPsicometrico

# Crear las tablas al iniciar la plataforma
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Finanzas con IA")

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"status": "Online", "plataforma": "Gestor Financiero Psicometrico"}

# INTERFAZ PARA INGRESAR DATOS (POST)
@app.post("/ingresar-gasto/")
def crear_gasto(descripcion: str, monto: float, nivel_satisfaccion: int, db: Session = Depends(get_db)):
    if nivel_satisfaccion < 1 or nivel_satisfaccion > 10:
        raise HTTPException(status_code=400, detail="La satisfaccion debe ser entre 1 y 10")
    
    # 1. Crear el movimiento
    nuevo_movimiento = Movimiento(tipo="GASTO", descripcion=descripcion, monto=monto)
    db.add(nuevo_movimiento)
    db.commit()
    db.refresh(nuevo_movimiento)
    
    # 2. Crear la métrica vinculada
    nueva_metrica = MetricaSatisfaccion(movimiento_id=nuevo_movimiento.id, nivel=nivel_satisfaccion)
    db.add(nueva_metrica)
    db.commit()
    
    return {"status": "exito", "id": nuevo_movimiento.id, "mensaje": "Gasto registrado con IA"}

# INTERFAZ PARA VER ANALISIS (GET)
@app.get("/ia/diagnostico")
def obtener_diagnostico(db: Session = Depends(get_db)):
    motor = MotorPsicometrico(db)
    return motor.calcular_costo_insatisfaccion()

