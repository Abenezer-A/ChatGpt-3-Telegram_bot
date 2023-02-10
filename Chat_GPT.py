import logging
import os

from telegram import ReplyKeyboardMarkup, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import openai

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
SELECT_ACTION, SEND_MESSAGE = range(2)

# OpenAI API Key
openai.api_key = os.environ['OPEN_AI']

# Define the reply keyboard to present the user with options
reply_keyboard = [['Send Message']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def start(update, context):
    update.message.reply_text("Hi! I am a full-featured ChatGPT Telegram bot. How can I help you today?", reply_markup=markup)
    return SELECT_ACTION

def select_action(update, context):
    selected_option = update.message.text
    if selected_option == 'Send Message':
        update.message.reply_text("Please enter the message you would like me to generate a response for.")
        return SEND_MESSAGE
    else:
        update.message.reply_text("Invalid option selected. Please try again.")
        return SELECT_ACTION

def send_message(update, context):
    user_message = update.message.text
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt='User: ' + user_message + '\n' + 'ChatGPT: ',
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    update.message.reply_text(message)
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Goodbye! If you need me again, don't hesitate to call.")
    return ConversationHandler.END

# Define the ConversationHandler and pass it the relevant handlers
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SELECT_ACTION: [MessageHandler(Filters.regex('^(Send Message)$'), select_action)],
        SEND_MESSAGE: [MessageHandler(Filters.text, send_message)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Get the API Key from the environment
TELEGRAM_API_KEY = os.environ['TELEGRAM_BOT']

# Create the Updater and pass it the API Key
updater = Updater(TELEGRAM_API_KEY, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Add the conversation handler to the dispatcher
dispatcher.add_handler(conversation_handler)

# Start the bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
