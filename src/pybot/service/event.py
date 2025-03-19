from typing import List, Dict
from chatgpt_service import ChatGPTService
from user_service import UserProfile

class EventService:
    def __init__(self, chatgpt_service: ChatGPTService):
        self.chatgpt_service = chatgpt_service

    def recommend_events(self, user_profile: UserProfile) -> List[Dict[str, str]]:
        """Recommend fictional events based on user's interests and description using ChatGPT."""
        if not user_profile.interests:
            return []

        # Craft a detailed prompt using both interests and description
        interests_str = ", ".join(user_profile.interests)
        prompt = (
            "You are an event planner. Generate a list of 3 fictional online events tailored to a user with the following profile:\n"
            f"Interests: {interests_str}\n"
            f"Description: {user_profile.description or 'No additional context provided.'}\n\n"
            "For each event, include the event name, date (in 2025), and a fake URL. Ensure the events align with the user's specific preferences. "
            "Format your response as a numbered list like this:\n"
            "1. Event Name - Date - URL\n"
            "2. Event Name - Date - URL\n"
            "3. Event Name - Date - URL"
        )

        # Get response from ChatGPT
        response = self.chatgpt_service.submit(prompt)
        if "Error" in response:
            return []

        # Parse ChatGPT's response into a list of events
        events = []
        try:
            for line in response.strip().split("\n"):
                if line.strip() and line[0].isdigit():
                    parts = line.split(" - ")
                    if len(parts) == 3:
                        name, date, url = parts
                        events.append({"name": name[3:].strip(), "date": date.strip(), "link": url.strip()})
        except Exception as e:
            return []  # Fallback to empty list if parsing fails

        return events