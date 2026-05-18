import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = [7790388507, 8372332318]


# =========================
# START
# =========================
async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)
    await update.message.reply_text("TOBY activo 😎")


# =========================
# CLIENTE
# =========================
async def cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):

    from app.database import SessionLocal
    from app.models import Prestamo, Pago

    if update.effective_chat.id not in ADMIN_ID:
        await update.message.reply_text("No autorizado")
        return

    if not context.args:
        await update.message.reply_text("Usa: /cliente nombre")
        return

    nombre = context.args[0]

    db = SessionLocal()

    try:
        prestamo = db.query(Prestamo).filter(
            Prestamo.cliente == nombre
        ).first()

        if not prestamo:
            await update.message.reply_text("Cliente no encontrado")
            return

        pagos = db.query(Pago).filter(
            Pago.prestamo_id == prestamo.id
        ).all()

        restante = prestamo.deuda_total - prestamo.pagado

        mensaje = f"""
🏦 ESTADO DE CUENTA

👤 Cliente: {prestamo.cliente}
💰 Capital: S/{prestamo.monto}
📊 Total: S/{prestamo.deuda_total}
💵 Pagado: S/{prestamo.pagado}
📉 Restante: S/{restante}

Estado: {prestamo.estado}

🏦 Historial de pagos:
"""

        for pago in pagos:
            mensaje += f"\n• {pago.fecha_pago} → S/{pago.monto_pago}"

        await update.message.reply_text(mensaje)

    finally:
        db.close()


# =========================
# WEBHOOK (RAILWAY)
# =========================
PORT = int(os.environ.get("PORT", 8000))


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", inicio))
    app.add_handler(CommandHandler("cliente", cliente))

    await app.initialize()

    # 🔥 IMPORTANTE: webhook en Railway
    await app.bot.set_webhook(
        url=f"https://TU-APP.up.railway.app/{TOKEN}"
    )

    await app.start()

    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN
    )

    print("BOT EN WEBHOOK ACTIVO 😎")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())