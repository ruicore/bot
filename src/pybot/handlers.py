import logging
from typing import Any, Self

from repository import RedisRepository
from service.chatgpt import ChatGPTService
from service.event import EventService
from service.user import UserService
from telegram import Update
from telegram.ext import CallbackContext


class TelegramCommandHandler:
    def __init__(
        self,
        redis_repo: RedisRepository,
        chatgpt_service: ChatGPTService,
        user_service: UserService,
        event_service: EventService,
    ):
        self.redis_repo = redis_repo
        self.chatgpt_service = chatgpt_service
        self.user_service = user_service
        self.event_service = event_service
        self.logger = logging.getLogger(__name__)

    def help(self, update: Update, _: CallbackContext[Any, Any, Any]) -> Self:
        update.message.reply_text('Commands: /help, /hello, /add, /register, /events')
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
            self.logger.error('Error in add command: %s', str(e))
            update.message.reply_text('An error occurred.')
        return self

    def register(self, update: Update, context: CallbackContext[Any, Any, Any]) -> Self:
        username = update.message.from_user.username or str(update.message.from_user.id)
        if not context.args:
            update.message.reply_text('Usage: /register <interests> (e.g., gaming vr social)')
            return self

        interests = context.args
        self.user_service.register_user(username, interests)
        matches = self.user_service.find_matches(username)

        response = f"Registered interests: {', '.join(interests)}.\n"
        if matches:
            response += f"Matched users: {', '.join(matches)}"
        else:
            response += 'No matches found yet. Invite friends to join!'
        update.message.reply_text(response)
        return self

    def events(self, update: Update, context: CallbackContext[Any, Any, Any]) -> Self:
        username = update.message.from_user.username or str(update.message.from_user.id)
        interests = self.user_service.get_user_interests(username)

        if not interests:
            update.message.reply_text('Please register your interests first with /register')
            return self

        events = self.event_service.recommend_events(interests)
        if not events:
            update.message.reply_text("Sorry, I couldn't generate event recommendations right now.")
            return self

        response = 'Recommended Events:\n'
        for event in events:
            response += f"- {event['name']} on {event['date']} ({event['link']})\n"
        update.message.reply_text(response)
        return self

    def handle_message(self, update: Update, context: CallbackContext[Any, Any, Any]) -> Self:
        reply = self.chatgpt_service.submit(update.message.text)
        self.logger.info('ChatGPT response: %s', reply)
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
        return self
