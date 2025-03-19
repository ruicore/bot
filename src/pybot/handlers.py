import logging
from typing import Any, Self

from chatgpt import ChatGPTService
from repository import RedisRepository
from telegram import Update
from telegram.ext import CallbackContext


class TelegramCommandHandler:
    def __init__(self, redis_repo: RedisRepository, chatgpt_service: ChatGPTService):
        self.redis_repo = redis_repo
        self.chatgpt_service = chatgpt_service
        self.logger = logging.getLogger(__name__)

    def help(self, update: Update, _: CallbackContext[Any, Any, Any]) -> Self:
        update.message.reply_text('Helping you helping you.')

        return self

    def hello(self, update: Update, context: CallbackContext[Any, Any, Any]) -> Self:
        reply_message = ' '.join(context.args) if context.args else 'friend'
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Good day, {reply_message}!')

        return self

    def add(self, update: Update, context: CallbackContext[Any, Any, Any]) -> Self:
        try:
            msg = context.args[0]
            self.logger.info('Incrementing count for: %s', msg)
            count = self.redis_repo.incr(msg)
            update.message.reply_text(f'You have said {msg} for {count} times')
        except IndexError:
            update.message.reply_text('Usage: /add <keyword>')
        except Exception as e:
            self.logger.error('Error in add command: %s', e)
            update.message.reply_text('An error occurred.')

        return self

    def handle_message(self, update: Update, context: CallbackContext[Any, Any, Any]) -> Self:
        reply = self.chatgpt_service.submit(update.message.text)
        self.logger.info('ChatGPT response: %s', reply)
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

        return self
