import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


try:
    api_key = st.secrets['GOOGLE_API_KEY']
    if not api_key:
        raise ValueError("API key for Google Generative AI is missing.")
    genai.configure(api_key=api_key)
except Exception as e:
    logging.error(f"Error configuring Generative AI: {e}")
    raise

try:
    model = genai.GenerativeModel("gemini-1.0-pro-latest")
except Exception as e:
    logging.error(f"Error initializing Generative Model: {e}")
    raise

def gemini_call(prompt, candidate_count=1, max_output_tokens=50, temperature=0.8):
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                candidate_count=candidate_count,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
            ),    
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        return response.text
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        return "An error occurred while generating content. Please try again later."