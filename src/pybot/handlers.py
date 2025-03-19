import logging
from typing import Any

from repository import RedisRepository
from service import ChatGPTService, EventService, UserService
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

    def help(self, update: Update, _: CallbackContext[Any, Any, Any]) -> None:
        update.message.reply_text(
            'Commands: /help, /hello, /add, /register, /events, /more_events\n'
            "Example: /register gaming vr \"I enjoy fast-paced shooter games\""
        )

    def hello(self, update: Update, context: CallbackContext[Any, Any, Any]) -> None:
        reply_message = ' '.join(context.args) if context.args else 'friend'
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Good day, {reply_message}!')

    def add(self, update: Update, context: CallbackContext[Any, Any, Any]) -> None:
        try:
            msg = context.args[0]
            self.logger.info(f'Incrementing count for: {msg}')
            count = self.redis_repo.incr(msg)
            update.message.reply_text(f'You have said {msg} for {count} times')
        except IndexError:
            update.message.reply_text('Usage: /add <keyword>')
        except Exception as e:
            self.logger.error(f'Error in add command: {e}')
            update.message.reply_text('An error occurred.')

    def register(self, update: Update, context: CallbackContext[Any, Any, Any]) -> None:
        username = update.message.from_user.username or str(update.message.from_user.id)
        if not context.args:
            update.message.reply_text(
                "Usage: /register <interests> [\"description\"] (e.g., /register gaming vr \"I enjoy FPS games\")"
            )
            return

        args = context.args
        interests = []
        description = ''
        for i, arg in enumerate(args):
            if arg.startswith('"') and arg.endswith('"'):
                description = arg[1:-1]
                interests = args[:i]
                break
            elif arg.startswith('"'):
                description = ' '.join(args[i:])[1:-1]
                interests = args[:i]
                break
            interests.append(arg)

        if not interests:
            update.message.reply_text('Please provide at least one interest.')
            return

        self.user_service.register_user(username, interests, description)
        matches = self.user_service.find_matches(username)

        response = f"Registered interests: {', '.join(interests)}"
        if description:
            response += f'\nDescription: {description}'
        response += '\n'
        if matches:
            response += f"Matched users: {', '.join(matches)}"
        else:
            response += 'No matches found yet. Invite friends to join!'
        update.message.reply_text(response)

    def events(self, update: Update, context: CallbackContext[Any, Any, Any]) -> None:
        username = update.message.from_user.username or str(update.message.from_user.id)
        user_profile = self.user_service.users.get(username)

        if not user_profile or not user_profile.interests:
            update.message.reply_text('Please register your interests first with /register')
            return

        events = self.event_service.recommend_events(user_profile)
        if not events:
            update.message.reply_text("Sorry, I couldn't generate event recommendations right now.")
            return

        response = 'Recommended Events:\n'
        for event in events:
            response += f"- {event['name']} on {event['date']} ({event['link']})\n"
        update.message.reply_text(response)

    def more_events(self, update: Update, context: CallbackContext[Any, Any, Any]) -> None:
        username = update.message.from_user.username or str(update.message.from_user.id)
        user_profile = self.user_service.users.get(username)

        if not user_profile or not user_profile.interests:
            update.message.reply_text('Please register your interests first with /register')
            return

        events = self.event_service.recommend_more_events(user_profile)
        if not events:
            update.message.reply_text("Sorry, I couldn't generate more event recommendations right now.")
            return

        response = 'More Recommended Events:\n'
        for event in events:
            response += f"- {event['name']} on {event['date']} ({event['link']})\n"
        update.message.reply_text(response)

    def handle_message(self, update: Update, context: CallbackContext[Any, Any, Any]) -> None:
        reply = self.chatgpt_service.submit(update.message.text)
        self.logger.info(f'ChatGPT response: {reply}')
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
