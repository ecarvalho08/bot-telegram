import os
import anthropic
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

historicos = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    historicos[update.effective_user.id] = []
    await update.message.reply_text("Olá! Sou seu assistente. Como posso ajudar?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text
    if user_id not in historicos:
        historicos[user_id] = []
    historicos[user_id].append({"role": "user", "content": texto})
    if len(historicos[user_id]) > 20:
        historicos[user_id] = historicos[user_id][-20:]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system="Você é um assistente útil e direto. Responda em português.",
        messages=historicos[user_id]
    )
    resposta = response.content[0].text
    historicos[user_id].append({"role": "assistant", "content": resposta})
    await update.message.reply_text(resposta)

async def limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    historicos[update.effective_user.id] = []
    await update.message.reply_text("Histórico limpo!")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("limpar", limpar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
