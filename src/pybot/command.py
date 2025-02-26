import logging
from typing import Any

from telegram import Update
from telegram.ext import CallbackContext

from pybot.chatgpt import chatgpt
from pybot.repository import repo


def help_command(update: Update, _: CallbackContext[Any, Any, Any]) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def echo(update: Update, context: CallbackContext[Any, Any, Any]):
    reply_message = update.message.text.upper()
    logging.info('Update: %s', update)
    logging.info('Context: %s', context)
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)  # type:ignore


def add(update: Update, context: CallbackContext[Any, Any, Any]) -> None:
    """Send a message when the command /add is issued."""
    try:
        msg = context.args[0]  # type:ignore
        logging.info(msg)
        repo.incr(msg)
        update.message.reply_text(f'You have said {msg} for {repo.get(msg)} times')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
    except Exception as e:
        logging.error(e)


def equipped_chatgpt(update: Update, context: CallbackContext[Any, Any, Any]) -> None:
    reply_message = chatgpt.submit(update.message.text)
    logging.info('Update: %s', update)
    logging.info('Context: %s', context)
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)  # type:ignore
