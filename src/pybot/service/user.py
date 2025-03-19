import logging
from typing import Dict, List, Set

from pydantic import BaseModel


class UserInterest(BaseModel):
    username: str
    interests: Set[str]


class UserService:
    def __init__(self):
        self.users: Dict[str, UserInterest] = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized UserService with in-memory storage')

    def register_user(self, username: str, interests: List[str]) -> None:
        self.logger.info('Registering user %s with interests: %s', username, interests)
        self.users[username] = UserInterest(username=username, interests=set(interests))

    def find_matches(self, username: str) -> List[str]:
        self.logger.debug('Finding matches for user: %s', username)
        if username not in self.users:
            self.logger.warning('User %s not found in registry', username)
            return []

        current_user = self.users[username]
        matches = []
        for other_user in self.users.values():
            if other_user.username != username and current_user.interests & other_user.interests:
                matches.append(other_user.username)
        self.logger.info('Found %d matches for %s: %s', len(matches), username, matches)
        return matches

    def get_user_interests(self, username: str) -> Set[str]:
        self.logger.debug('Retrieving interests for user: %s', username)
        return self.users.get(username, UserInterest(username=username, interests=set())).interests
