from groq import Groq
import os
import streamlit as st

groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def groq_call(prompt):
    try:
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
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None