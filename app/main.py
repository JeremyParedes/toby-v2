from fastapi.responses import RedirectResponse
from fastapi import Form
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import requests

from groq import Groq

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app import schemas
from app.models import Prestamo, Pago

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="supersecretkey123",
    max_age=300,
)

USUARIO = "admin"
PASSWORD = "1234"

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("API KEY:", os.getenv("GROQ_API_KEY"))
print("API KEY:", os.getenv("YOUTUBE_API_KEY"))

YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicio
@app.get("/")
def inicio(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="inicio.html"
    )


@app.get("/banco")
def banco(request: Request):

    if "user" not in request.session:
        return RedirectResponse(
    url="/login",
    status_code=302
)

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# Crear préstamo
@app.post("/prestamos")
def crear_prestamo(
    prestamo: schemas.PrestamoCreate,
    db: Session = Depends(get_db)
):
    deuda_total = prestamo.monto + (
        prestamo.monto * prestamo.interes / 100
    )

    nuevo_prestamo = Prestamo(
        cliente=prestamo.cliente,
        monto=prestamo.monto,
        interes=prestamo.interes,
        deuda_total=deuda_total,
        pagado=0,
        estado=prestamo.estado
    )

    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)

    return nuevo_prestamo

# Ver todos
@app.get("/prestamos")
def listar_prestamos(db: Session = Depends(get_db)):
    return db.query(Prestamo).all()

# Buscar cliente
@app.get("/prestamos/{cliente}")
def buscar_cliente(cliente: str, db: Session = Depends(get_db)):
    prestamo = db.query(Prestamo).filter(
        Prestamo.cliente == cliente
    ).first()

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    restante = prestamo.deuda_total - prestamo.pagado

    return {
        "cliente": prestamo.cliente,
        "deuda_total": prestamo.deuda_total,
        "pagado": prestamo.pagado,
        "restante": restante,
        "estado": prestamo.estado
    }

# Registrar pago
@app.put("/prestamos/{id}/pagar")
def registrar_pago(
    id: int,
    pago: schemas.PagoCreate,
    db: Session = Depends(get_db)
):

    prestamo = db.query(Prestamo).filter(
        Prestamo.id == id
    ).first()

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail="Préstamo no encontrado"
        )

    nuevo_pago = Pago(
        prestamo_id=id,
        monto_pago=pago.monto_pago,
        fecha_pago=pago.fecha_pago
    )

    db.add(nuevo_pago)

    prestamo.pagado += pago.monto_pago

    restante = prestamo.deuda_total - prestamo.pagado

    if restante <= 0:
        prestamo.estado = "Pagado"

    db.commit()

    return {
        "mensaje": "Pago registrado",
        "fecha": pago.fecha_pago,
        "restante": restante
    }
@app.get("/prestamos/{id}/pagos")
def ver_pagos(id: int, db: Session = Depends(get_db)):

    pagos = db.query(Pago).filter(
        Pago.prestamo_id == id
    ).all()

    return pagos
@app.delete("/prestamos/{id}")
def eliminar_prestamo(
    id: int,
    db: Session = Depends(get_db)
):

    prestamo = db.query(Prestamo).filter(
        Prestamo.id == id
    ).first()

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail="Préstamo no encontrado"
        )

    pagos = db.query(Pago).filter(
        Pago.prestamo_id == id
    ).all()

    for pago in pagos:
        db.delete(pago)

    db.delete(prestamo)

    db.commit()

    return {
        "mensaje":"Préstamo eliminado"
    }

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):

    prestamos = db.query(Prestamo).all()

    total_prestado = 0
    total_pagado = 0
    total_pendiente = 0
    total_ganancia = 0

    for p in prestamos:

        total_prestado += p.deuda_total

        total_pagado += p.pagado

        total_pendiente += (
            p.deuda_total - p.pagado
        )

        ganancia = (
            p.deuda_total - p.monto
        )

        total_ganancia += ganancia

    return {
        "clientes": len(prestamos),
        "prestado": total_prestado,
        "pagado": total_pagado,
        "pendiente": total_pendiente,
        "ganancia": total_ganancia
    }

@app.post("/ia")
async def ia(request: Request):

    data = await request.json()
    texto = data["mensaje"]

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
                 {
                      "role": "system",
                        "content": """
                        Eres TOM.

                        Responde:
                        - máximo 10 a 20 palabras
                        - directo
                        - sin explicaciones
                        - estilo comando militar / IA
                        """
                }
        ]
    )

    return {
        "respuesta": respuesta.choices[0].message.content
    }
@app.post("/youtube")
async def youtube(data: dict):

    query = data["query"]

    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={query}&type=video&maxResults=1&key={YOUTUBE_KEY}"
    )

    r = requests.get(url)
    result = r.json()

    if "items" not in result or len(result["items"]) == 0:
        return {"url": None}

    video_id = result["items"][0]["id"]["videoId"]

    return {
        "url": f"https://www.youtube.com/watch?v={video_id}"
    }

@app.post("/youtube-search")
def youtube_search(data: dict):

    query = data["query"]
    api_key = os.getenv("YOUTUBE_API_KEY")

    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={query}&key={api_key}&type=video&maxResults=1"
    )

    response = requests.get(url)
    result = response.json()

    video_id = result["items"][0]["id"]["videoId"]

    return {
        "video_url": f"https://www.youtube.com/watch?v={video_id}"
    }

@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return {"mensaje": "Sesión cerrada"}
def verificar_login(request: Request):
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="No autorizado")

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    if username == USUARIO and password == PASSWORD:

        request.session["user"] = username

        response = RedirectResponse(
            url="/banco",
            status_code=302
        )

        return response

    return RedirectResponse(
        url="/login",
        status_code=302
    )   