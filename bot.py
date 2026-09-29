#pip install python-telegram-bot
# importamos el main.py 
# to run this code from terminal do: Aviation_app/Telegram_bot/bot.py (in other words: your working directory)
# cd "Aviation_app" : python -m Telegram_bot.bot
# Press Control + C to stop the bot from running / presiona control + c para detener el bot en la terminal
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from main import iniciar_vigilancia

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Hola, el bot funciona. Iniciando vigilancia..."
    )

    print(">>> TELEGRAM: iniciando iniciar_vigilancia()")
    resultado = iniciar_vigilancia()

    print(">>> TELEGRAM: iniciar_vigilancia() ha terminado")

    if resultado is not None:
        await update.message.reply_text(
            "Se ha detectado un posible accidente."
        )
        print(">>> TELEGRAM: mensaje de accidente enviado")
    else:
        await update.message.reply_text(
            "No se han detectado posibles accidentes."
        )
        print(">>> TELEGRAM: mensaje de no accidente enviado")
# -----------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------- WARNING ----------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------

#You need a token from BotFather (this token is yours and you cant share it with anybody)
TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
application = Application.builder().token(TOKEN).build()

application.add_handler(
    CommandHandler("start", start)
)

application.run_polling()