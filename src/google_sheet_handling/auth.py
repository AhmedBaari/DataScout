import streamlit as st
import google_auth_oauthlib.flow

def authenticate_with_google():
    client_secrets = {
        "web": {
            "client_id": st.secrets["google"]["client_id"],
            "project_id": st.secrets["google"]["project_id"],
            "auth_uri": st.secrets["google"]["auth_uri"],
            "token_uri": st.secrets["google"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["google"]["client_secret"],
            "redirect_uris": st.secrets["google"]["redirect_uris"],
            "javascript_origins": st.secrets["google"]["javascript_origins"]
        }
    }

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_secrets,
        scopes=["https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/spreadsheets"]
    )
    flow.redirect_uri = "http://localhost:8501"
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"[Sign in with Google]({auth_url})", unsafe_allow_html=True)

    return flow