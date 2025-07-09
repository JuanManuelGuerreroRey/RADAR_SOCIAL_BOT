import os
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
)

TOKEN = "8138364362:AAHYdeTeSFVuCWvu_PGkQ9GLzBSYh8GejRQ"
GRUPO_ID = -1001169225264
MI_ID = 7887249011

messages = []
replies = defaultdict(list)

def guardar_datos():
    with open("interacciones.json", "w") as f:
        json.dump(messages, f)

def cargar_datos():
    global messages
    try:
        with open("interacciones.json", "r") as f:
            messages = json.load(f)
    except:
        messages = []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.chat_id == GRUPO_ID:
        msg = update.message
        messages.append({
            "user": msg.from_user.first_name,
            "user_id": msg.from_user.id,
            "text": msg.text,
            "reply_to": msg.reply_to_message.from_user.first_name if msg.reply_to_message else None,
            "timestamp": msg.date.isoformat(),
            "chat_id": msg.chat_id
        })
        guardar_datos()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        await update.message.reply_text("🤖 Bot encendido. Usa /help para ver comandos.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        await update.message.reply_text(
            "/menciones_juan - Quién menciona más a Juan
"
            "/ranking_menciones - Quién menciona más a quién
"
            "/top_respuestas - Quién responde más a quién
"
            "/pareja_dia - Pareja del día
"
            "/pareja_semana - Pareja de la semana
"
            "/pareja_mes - Pareja del mes
"
            "/frases_populares - Frases más repetidas
"
            "/stats - Actividad de usuarios
"
            "/resumen - Resumen conversacional del día
"
            "/raw - Cantidad de mensajes almacenados"
        )

async def menciones_juan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        contador = Counter()
        for m in messages:
            if "Juan" in m["text"]:
                contador[m["user"]] += m["text"].count("Juan")
        if contador:
            texto = "
".join([f"{u}: {c}" for u, c in contador.most_common()])
            await update.message.reply_text(f"👀 Menciones a Juan:
{texto}")
        else:
            await update.message.reply_text("Nadie ha mencionado a Juan.")

async def ranking_menciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        menciones = Counter()
        for m in messages:
            for nombre in [u["user"] for u in messages if u["user"] != m["user"]]:
                if nombre in m["text"]:
                    menciones[(m["user"], nombre)] += 1
        if menciones:
            top = menciones.most_common(5)
            texto = "
".join([f"{a} menciona a {b} ({c} veces)" for (a, b), c in top])
            await update.message.reply_text("📌 Ranking de menciones:
" + texto)
        else:
            await update.message.reply_text("No hay menciones entre usuarios registradas.")

async def top_respuestas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        conteo = Counter((m['user'], m['reply_to']) for m in messages if m['reply_to'])
        if conteo:
            texto = "
".join([f"{u} → {r} ({c} respuestas)" for (u, r), c in conteo.most_common(5)])
            await update.message.reply_text("🔁 Top respuestas:
" + texto)
        else:
            await update.message.reply_text("No hay respuestas aún.")

async def pareja_periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        comando = update.message.text[1:]
        ahora = datetime.utcnow()
        if comando == "pareja_dia":
            desde = ahora - timedelta(days=1)
        elif comando == "pareja_semana":
            desde = ahora - timedelta(days=7)
        elif comando == "pareja_mes":
            desde = ahora - timedelta(days=30)
        else:
            return
        interacciones = Counter()
        for m in messages:
            if m['reply_to'] and datetime.fromisoformat(m['timestamp']) > desde:
                pareja = tuple(sorted([m['user'], m['reply_to']]))
                interacciones[pareja] += 1
        if interacciones:
            top = interacciones.most_common(1)[0]
            await update.message.reply_text(f"💘 Pareja destacada: {top[0][0]} y {top[0][1]} ({top[1]} interacciones)")
        else:
            await update.message.reply_text("Sin interacciones suficientes para el período.")

async def frases_populares(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        frases = Counter(m['text'] for m in messages if m['text'])
        top = frases.most_common(3)
        texto = "
".join([f"“{fr}” ({c} veces)" for fr, c in top])
        await update.message.reply_text("💬 Frases más repetidas:
" + texto)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        conteo = Counter(m['user'] for m in messages)
        total = sum(conteo.values())
        top = conteo.most_common(5)
        texto = "
".join([f"{u}: {c} mensajes" for u, c in top])
        await update.message.reply_text(f"📊 Actividad del grupo:
{texto}
Total: {total} mensajes")

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        hoy = datetime.utcnow().date()
        textos = [m['text'] for m in messages if datetime.fromisoformat(m['timestamp']).date() == hoy]
        resumen = " ".join(textos[-20:])  # últimos mensajes para resumir
        resumen = resumen[:300] + "..." if len(resumen) > 300 else resumen
        await update.message.reply_text(f"📝 Resumen del día:
{resumen}")

async def raw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        await update.message.reply_text(f"📦 Mensajes almacenados: {len(messages)}")

if __name__ == "__main__":
    cargar_datos()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menciones_juan", menciones_juan))
    app.add_handler(CommandHandler("ranking_menciones", ranking_menciones))
    app.add_handler(CommandHandler("top_respuestas", top_respuestas))
    app.add_handler(CommandHandler("pareja_dia", pareja_periodo))
    app.add_handler(CommandHandler("pareja_semana", pareja_periodo))
    app.add_handler(CommandHandler("pareja_mes", pareja_periodo))
    app.add_handler(CommandHandler("frases_populares", frases_populares))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("resumen", resumen))
    app.add_handler(CommandHandler("raw", raw))

    app.run_polling()
