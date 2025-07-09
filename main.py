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
        await update.message.reply_text("🤖 Radar Social Bot PRO activo y registrando. Usa /help para ver comandos.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        await update.message.reply_text(
            "/menciones_juan - Quién menciona más a Juan\n"
            "/ranking_menciones - Quién menciona a quién\n"
            "/resumen_dia - Resumen analizado del grupo\n"
            "/top_respuestas - Quién responde a quién\n"
            "/pareja_dia - Pareja del día\n"
            "/pareja_semana - Pareja de la semana\n"
            "/pareja_mes - Pareja del mes\n"
            "/frases_populares - Frases más repetidas\n"
            "/stats - Estadísticas del grupo\n"
            "/raw - Ver datos crudos"
        )

async def menciones_juan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        contador = Counter()
        for m in messages:
            if "Juan" in m["text"]:
                contador[m["user"]] += m["text"].count("Juan")
        if contador:
            texto = "\n".join([f"{u}: {c} menciones" for u, c in contador.most_common(5)])
            await update.message.reply_text(f"👤 Menciones a Juan:\n{texto}")
        else:
            await update.message.reply_text("Nadie ha mencionado a Juan todavía.")

async def ranking_menciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        menciones = Counter()
        for m in messages:
            for other in {x["user"] for x in messages if x["user"] != m["user"]}:
                if other in m["text"]:
                    menciones[(m["user"], other)] += 1
        if menciones:
            top = menciones.most_common(5)
            texto = "\n".join([f"{a} menciona a {b}: {c} veces" for (a, b), c in top])
            await update.message.reply_text(f"🔁 Ranking de menciones:\n{texto}")
        else:
            await update.message.reply_text("No hay suficientes menciones entre usuarios.")

async def top_respuestas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        conteo = Counter(m['reply_to'] for m in messages if m['reply_to'])
        if conteo:
            top = conteo.most_common(1)[0]
            await update.message.reply_text(f"La persona que más recibe respuestas es {top[0]} con {top[1]} respuestas.")
        else:
            await update.message.reply_text("Aún no hay respuestas registradas.")

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
            await update.message.reply_text("Comando no reconocido.")
            return

        interacciones = Counter()
        for m in messages:
            if m['reply_to'] and datetime.fromisoformat(m['timestamp']) > desde:
                pareja = tuple(sorted([m['user'], m['reply_to']]))
                interacciones[pareja] += 1

        if interacciones:
            top = interacciones.most_common(1)[0]
            await update.message.reply_text(f"💘 Pareja destacada: {top[0][0]} y {top[0][1]} con {top[1]} interacciones.")
        else:
            await update.message.reply_text("No hay suficientes interacciones para determinar una pareja.")

async def frases_populares(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        frases = Counter(m['text'] for m in messages if m['text'])
        top = frases.most_common(3)
        if top:
            texto = "\n".join([f"✨ {frase} ({conteo} veces)" for frase, conteo in top])
            await update.message.reply_text(f"Frases más repetidas:\n{texto}")
        else:
            await update.message.reply_text("No hay frases registradas.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        conteo = Counter(m['user'] for m in messages)
        total = sum(conteo.values())
        top = conteo.most_common(3)
        texto = "\n".join([f"{u}: {c} mensajes" for u, c in top])
        await update.message.reply_text(f"📊 Top 3 usuarios activos:\n{texto}\nTotal mensajes: {total}")

async def raw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        await update.message.reply_text(f"📦 Datos almacenados: {len(messages)} mensajes")

async def resumen_dia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MI_ID:
        hoy = datetime.utcnow().date()
        textos = [m['text'] for m in messages if datetime.fromisoformat(m['timestamp']).date() == hoy and m['text']]
        resumen = " ".join(textos)
        resumen_corto = resumen[:300] + "..." if len(resumen) > 300 else resumen
        await update.message.reply_text(f"📘 Resumen de hoy:\n{resumen_corto if resumen_corto else 'No hay mensajes hoy.'}")

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
    app.add_handler(CommandHandler("raw", raw))
    app.add_handler(CommandHandler("resumen_dia", resumen_dia))

    app.run_polling()
