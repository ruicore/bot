import requests

from setting import ChatGPT, config


class HKBUChatGPT:
    gpt: ChatGPT = config.chatgpt

    def submit(self, message):

        url = (
            f'{self.gpt.basicurl}/deployments/{self.gpt.modelname}/chat/completions/?api-version={self.gpt.apiversion}'
        )
        response = requests.post(
            url,
            json={'messages': [{'role': 'user', 'content': message}]},
            headers={
                'Content-Type': 'application/json',
                'api-key': self.gpt.access_token,
            },
            timeout=120,
        )

        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response


chatgpt = HKBUChatGPT()

if __name__ == '__main__':
    while True:
        user_input = input('Typing anything to ChatGPT:\t')
        resp = chatgpt.submit(user_input)
        print(resp)
