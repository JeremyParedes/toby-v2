from app.database import SessionLocal
from app.models import Prestamo, Pago

from telegram import Update

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

ADMIN_ID = 123456789


async def inicio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print(update.effective_chat.id)

    await update.message.reply_text(
        "TOBY activo 😎"
    )


# 👇 MOVER ESTA FUNCIÓN ARRIBA
async def cliente(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.id != ADMIN_ID:

        await update.message.reply_text(
            "No autorizado"
        )

        return
    
    if not context.args:

        await update.message.reply_text(
            "Usa: /cliente nombre"
        )

        return

    nombre = context.args[0]

    db = SessionLocal()

    prestamo = db.query(Prestamo).filter(
        Prestamo.cliente == nombre
    ).first()

    if not prestamo:

        await update.message.reply_text(
            "Cliente no encontrado"
        )

        return

    pagos = db.query(Pago).filter(
        Pago.prestamo_id == prestamo.id
    ).all()

    restante = (
        prestamo.deuda_total -
        prestamo.pagado
    )

    mensaje = f"""
🏦ESTADO DE CUENTA:

👤Cliente {prestamo.cliente}
💰Capital: S/{prestamo.monto}
📊 Total: S/{prestamo.deuda_total}
💵Pagado: S/{prestamo.pagado}
📉Restante: S/{restante}

Estado: {prestamo.estado}

🏦Historial de pagos:
"""

    for pago in pagos:

        mensaje += (
            f"\n• {pago.fecha_pago}"
            f" → S/{pago.monto_pago}"
        )

    await update.message.reply_text(mensaje)


# 👇 APP ABAJO
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", inicio)
)

app.add_handler(
    CommandHandler("cliente", cliente)
)

print("BOT TOBY ENCENDIDO 😎")

app.run_polling()