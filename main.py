import freecurrencyapi
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from decouple import config

from exceptions import InvalidCurrenciesException
from logging_bot import logger
from validators import validate_currencies


API_TOKEN = config('TOKEN')
API_KEY = config('API_KEY')
client = freecurrencyapi.Client(API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(f"User {user.username} started the bot.")
    await update.message.reply_html(
        f"Привет, {user.mention_html()}"
    )


async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /convert is issued."""
    result = update.message.text.split(maxsplit=2)
    if len(result) == 3 and result[1].replace('.', '', 1).isdigit():
        amount = float(result[1])
        operation = result[-1].upper().split()
        user = update.effective_user
        logger.info(f"User {user.username} requested conversion: {amount} {operation[0]} to {operation[-1]}")
        try:
            await validate_currencies(client, operation)
            currencies = client.latest(currencies=[operation[0], operation[-1]])
            result = amount * (currencies['data'][operation[-1]] / currencies['data'][operation[0]])
            await update.message.reply_html(f'{round(result, 2)} {operation[-1]}')
        except InvalidCurrenciesException:
            logger.error(f"User {user.username} provided invalid currencies.")
            await update.message.reply_html('Упс! Вы ввели неккоректное название валют.')
    else:
        logger.warning("Invalid request received.")
        await update.message.reply_html('Неккоректный запрос.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Доступные команды:\n"
                                    "/convert - конвертация (Например: /convert 100 USD to EUR)")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message with greetings or farewells based on context."""
    message_text = update.message.text.lower()

    greetings = ["привет", "добрый", "здравствуйте"]
    farewells = ["пока", "до свидания", "бай"]
    gratitude = ["спасибо", "пасиба", "от души"]

    is_greeting = any(greeting in message_text for greeting in greetings)
    is_farewell = any(farewell in message_text for farewell in farewells)
    is_gratitude = any(thanks in message_text for thanks in gratitude)

    if is_greeting:
        response = "Здравствуйте! Вас приветствует бот-конвертер! Для ознакомления перейдите в /help"
    elif is_farewell:
        response = "До свидания. Ждём вашего возвращения"
    elif is_gratitude:
        response = "Всегда рады помочь!"
    else:
        response = "Прошу прощения, я не понимаю. Для ознакомления с командами перейдите в /help"

    await update.message.reply_text(response)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(API_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("convert", convert_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
