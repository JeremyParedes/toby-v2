from pydantic import BaseModel

class PrestamoCreate(BaseModel):
    cliente: str
    monto: float
    interes: float
    estado: str

class PagoCreate(BaseModel):
    monto_pago: float

class PrestamoResponse(BaseModel):
    id: int
    cliente: str
    monto: float
    interes: float
    deuda_total: float
    pagado: float
    estado: str

    class Config:
        from_attributes = True
        
class PagoCreate(BaseModel):
    monto_pago: float
    fecha_pago: str        