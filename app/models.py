from sqlalchemy import Column, Integer, String, Float
from app.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime 

class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, index=True)
    monto = Column(Float)
    interes = Column(Float)
    deuda_total = Column(Float)
    pagado = Column(Float, default=0)
    estado = Column(String)

    pagos = relationship("Pago", back_populates="prestamo")


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    prestamo_id = Column(Integer, ForeignKey("prestamos.id"))
    monto_pago = Column(Float)
    fecha_pago = Column(String)

    prestamo = relationship("Prestamo", back_populates="pagos")    

