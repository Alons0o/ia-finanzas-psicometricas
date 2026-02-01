from app.db.session import Session
from app.models.movimiento import Movimiento

def listar_movimientos():
    session = Session()
    try:
        movimientos = session.query(Movimiento).all()
        return movimientos
    finally:
        session.close()
