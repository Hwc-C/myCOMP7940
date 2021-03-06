from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import configparser
import logging
import redis

global redis1

def internet_on(TOKEN):
	try:
		response=urllib2.urlopen('https://api.telegram.org/bot{}/getUpdates'.format(TOKEN),timeout=1)
		return True
	except urllib2.URLError as err: 
		pass
		return False

def main():
    # Load your token and create an Updater for your Bot
    
    config = configparser.ConfigParser()
    config.read('config.ini')
	
	# internet_on((config['TELEGRAM']['ACCESS_TOKEN']))

    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    
    # establish a connection to the redis server
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PWD']), port=(config['REDIS']['PORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("decr", decr))
    dispatcher.add_handler(CommandHandler("del", delete))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))


    # To start the bot:
    updater.start_polling()
    updater.idle()

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def decr(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /decr is issued."""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /decr keyword <-- this should store the keyword
        redis1.decr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /decr <keyword>')


def delete(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /delete is issued."""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /delete keyword <-- this should store the keyword
        redis1.delete(msg)
        update.message.reply_text('You have deleted ' + msg)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /del <keyword>')


def hello_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello <name> is issued"""
    try:
        update.message.reply_text('Good day, {}!'.format(context.args[0]))
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <name>')
	


if __name__ == '__main__':
    main()
