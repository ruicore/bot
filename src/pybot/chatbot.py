import logging

from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater

from pybot.command import add, equipped_chatgpt, help_command
from pybot.setting import config


def main():
    updater = Updater(token=config.telegram.access_token, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    dispatcher.add_handler(CommandHandler('add', add))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), equipped_chatgpt))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
