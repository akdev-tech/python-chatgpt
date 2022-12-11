import uuid
import json

import config
from auth import Auth
from errors import ResponseError


class Stream:
    def __init__(self, session):
        self.session = session

    def _process_chunks(self, chunks):
        if type(chunks) == bytes:
            chunks = chunks.decode()
            chunks = chunks.split("\n\n")
        elif type(chunks) == list:
            chunks = [c.decode() for c in chunks]
        else:
            raise ResponseError("Unknown response")
        chunks = [c for c in chunks if c and "message" in c]
        if not chunks:
            raise ResponseError("No response in stream")
        chunk = chunks[-1]
        chunk = chunk.replace("data: ", "").strip()
        chunk = json.loads(chunk)
        return chunk.get("message", {}).get("content", {}).get("parts", [None])[0]

    def send_message(self, message):
        token = Auth.get_token(self.session)

        self.session.headers.update({
            "accept": "text/event-stream",
            "X-OpenAI-Assistant-App-Id": "",
            "Authorization": f"Bearer {token}"
        })

        params = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": {
                        "content_type": "text",
                        "parts": [message]
                    }
                }
            ],
            "parent_message_id": "",
            "model": config.model
        }

        with self.session.stream(
            "POST", "https://chat.openai.com/backend-api/conversation",
            json=params, headers={"content-type": "application/json"},
            timeout=None
        ) as response:
            chunks = []
            for chunk in response.iter_bytes():
                chunks.append(chunk)

            response = self._process_chunks(chunks)
            return response
