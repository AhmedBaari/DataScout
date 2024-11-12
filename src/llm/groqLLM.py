from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def groq_call(prompt):
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-70b-versatile",
        stream=False,
    )

    return chat_completion.choices[0].message.content