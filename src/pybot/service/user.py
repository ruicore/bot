from typing import Dict, List, Set

from pydantic import BaseModel

from .chatgpt import ChatGPTService


class UserProfile(BaseModel):
    username: str
    interests: Set[str]
    description: str = ''


class UserService:
    def __init__(self, chatgpt_service: ChatGPTService):
        self.chatgpt_service = chatgpt_service
        self.users: Dict[str, UserProfile] = {}

    def register_user(self, username: str, interests: List[str], description: str = '') -> None:
        self.users[username] = UserProfile(username=username, interests=set(interests), description=description.strip())

    def find_matches(self, username: str) -> List[str]:
        if username not in self.users:
            return []

        current_user = self.users[username]
        other_users = [u for u in self.users.values() if u.username != username]
        if not other_users:
            return []

        prompt = (
            'You are a matchmaking assistant. I have a user with the following profile:\n'
            f"Interests: {', '.join(current_user.interests)}\n"
            f"Description: {current_user.description or 'No additional context provided.'}\n\n"
            'Here are other user profiles:\n'
        )
        for i, user in enumerate(other_users, 1):
            prompt += (
                f'User {i}:\n'
                f"Interests: {', '.join(user.interests)}\n"
                f"Description: {user.description or 'No additional context provided.'}\n"
            )
        prompt += (
            '\nBased on the interests and descriptions, suggest up to 3 users who are the best matches '
            'for the first user. Provide their user numbers (e.g., User 1, User 2) and a brief reason '
            'for each match. Format your response as:\n'
            '- User X: [reason]\n'
            '- User Y: [reason]\n'
            '- User Z: [reason]'
        )

        response = self.chatgpt_service.submit(prompt)
        if 'Error' in response:
            return []

        matches = []
        try:
            for line in response.strip().split('\n'):
                if line.startswith('- User'):
                    user_num = int(line.split(':')[0].split('User')[1].strip()) - 1
                    if 0 <= user_num < len(other_users):
                        matches.append(other_users[user_num].username)
        except Exception:
            return []

        return matches
