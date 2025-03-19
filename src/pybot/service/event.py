from typing import Dict, List

from .chatgpt import ChatGPTService


class EventService:
    def __init__(self, chatgpt_service: ChatGPTService):
        self.chatgpt_service = chatgpt_service

    def recommend_events(self, interests: set[str]) -> List[Dict[str, str]]:
        """Recommend fictional events based on user interests using ChatGPT."""
        if not interests:
            return []

        # Craft the prompt
        interests_str = ', '.join(interests)
        prompt = (
            f'Generate a list of 3 fictional online events for someone interested in {interests_str}. '
            'For each event, include the event name, date (in 2025), and a fake URL. '
            'Format your response as a numbered list like this:\n'
            '1. Event Name - Date - URL\n'
            '2. Event Name - Date - URL\n'
            '3. Event Name - Date - URL'
        )

        # Get response from ChatGPT
        response = self.chatgpt_service.submit(prompt)
        if 'Error' in response:
            return []

        # Parse ChatGPT's response into a list of events
        events = []
        try:
            for line in response.strip().split('\n'):
                if line.strip() and line[0].isdigit():
                    parts = line.split(' - ')
                    if len(parts) == 3:
                        name, date, url = parts
                        events.append({'name': name[3:].strip(), 'date': date.strip(), 'link': url.strip()})
        except Exception as e:
            return []  # Fallback to empty list if parsing fails

        return events
