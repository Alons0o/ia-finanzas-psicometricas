from sqlalchemy.orm import Session
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

class MotorPsicometrico:
    def __init__(self, db: Session):
        self.db = db

    def calcular_costo_insatisfaccion(self):
        """Busca gastos con satisfacción < 5 y suma el monto total."""
        gastos_ineficientes = (
            self.db.query(Movimiento)
            .join(MetricaSatisfaccion)
            .filter(MetricaSatisfaccion.nivel < 5)
            .all()
        )
        total_desperdiciado = sum(g.monto for g in gastos_ineficientes)
        
        return {
            "total_ineficiente": total_desperdiciado,
            "cantidad_gastos": len(gastos_ineficientes),
            "detalles": [
                {"desc": g.descripcion, "monto": g.monto, "nivel": g.satisfaccion.nivel}
                for g in gastos_ineficientes
            ]
        }

    def simular_alcance_meta(self, monto_meta: float, ahorro_mensual_base: float):
        """Calcula meses para alcanzar la meta con y sin recorte de gastos."""
        costo_info = self.calcular_costo_insatisfaccion()
        desperdicio_mensual = costo_info["total_ineficiente"]
        
        # Escenario A: Ahorro normal
        meses_normal = monto_meta / ahorro_mensual_base if ahorro_mensual_base > 0 else 0
        
        # Escenario B: Ahorro optimizado
        ahorro_optimizado = ahorro_mensual_base + desperdicio_mensual
        meses_optimizado = monto_meta / ahorro_optimizado if ahorro_optimizado > 0 else 0
        
        return {
            "monto_meta": monto_meta,
            "ahorro_recuperado": desperdicio_mensual,
            "meses_normal": round(meses_normal, 1),
            "meses_optimizado": round(meses_optimizado, 1),
            "tiempo_ahorrado": round(meses_normal - meses_optimizado, 1)
        }
    
    def preparar_datos_burbujas(self):
        """Prepara datos para el gráfico: X=Monto, Y=Satisfacción, Tamaño=Peso."""
        movimientos = self.db.query(Movimiento).join(MetricaSatisfaccion).all()
        total_gastos = sum(m.monto for m in movimientos if m.tipo == "GASTO") or 1
        
        datos = []
        for m in movimientos:
            if m.tipo == "GASTO":
                datos.append({
                    "descripcion": m.descripcion,
                    "monto": m.monto,
                    "satisfaccion": m.satisfaccion.nivel,
                    "peso": (m.monto / total_gastos) * 1000 # Para el tamaño de la burbuja
                })
        return datos
    