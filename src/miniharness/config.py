from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
MAX_STEPS = 5

client = Anthropic(    
    base_url=os.getenv("ENDPOINT"),
    api_key=os.getenv("API_KEY")
)