import google_auth_oauthlib.flow
import streamlit as st

def authenticate_with_google():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=["https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    flow.redirect_uri = "http://localhost:8501"
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"[Sign in with Google]({auth_url})", unsafe_allow_html=True)

    return flow