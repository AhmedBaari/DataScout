import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")


def gemini_call(prompt, candidate_count=1, max_output_tokens=50, temperature=0.8):
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            candidate_count=candidate_count,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        ),
    )
    return response.text