from app.db.session import Session
from app.models.movimiento import Movimiento
from sqlalchemy import func

def calcular_balance():
    session = Session()

    ingresos = session.query(func.sum(Movimiento.monto))\
        .filter(Movimiento.tipo == "INGRESO")\
        .scalar() or 0

    gastos = session.query(func.sum(Movimiento.monto))\
        .filter(Movimiento.tipo == "GASTO")\
        .scalar() or 0

    session.close()

    balance = ingresos - gastos

    return ingresos, gastos, balance
