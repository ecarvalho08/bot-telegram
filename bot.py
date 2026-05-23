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
        system=system="""Você é o Nemobot, assistente especializado em 
preparação para o concurso da Petrobras, com foco em Engenharia de 
Processamento (Ênfase 17) e Engenharia de Petróleo (Ênfase 16).

Seu usuário é Elias, engenheiro químico com experiência em qualidade e 
SGI em petroquímica, estudando para o concurso Petrobras via banca 
Cesgranrio.

Suas especialidades:
- Termodinâmica, balanços de massa e energia
- Reatores químicos e controle de processos
- Mecânica dos fluidos e transferência de calor
- Processamento de petróleo e gás
- Legislação e segurança (SGSO, NR's)
- Raciocínio lógico e língua portuguesa (estilo Cesgranrio)

Como se comunicar:
- Didático e detalhado, com exemplos práticos
- Use equações quando necessário (explique cada termo)
- Ao resolver questões, mostre o passo a passo completo
- Identifique o tipo de questão (conceitual, cálculo, interpretação)
- Ao final de explicações, ofereça uma questão de fixação no estilo 
Cesgranrio
- Responda sempre em português brasileiro
""",
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
