import os
from dotenv import load_dotenv
from config import client

load_dotenv()

def generate_answers(answer):
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role":"user",
                "content": answer
            }
        ],
        model=os.getenv("MODEL")
    )

    ans = message.content[0].text
    
    return ans