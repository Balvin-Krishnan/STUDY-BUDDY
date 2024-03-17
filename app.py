import os
from dotenv import load_dotenv
import openai
import streamlit


load_dotenv()

client = openai.OpenAI()

model = "gpt-3.5-turbo-0125"

# Upload file to OpenAI embedddings
