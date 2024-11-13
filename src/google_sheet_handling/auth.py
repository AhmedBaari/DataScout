import streamlit as st
import google_auth_oauthlib.flow

def authenticate_with_google():
    client_secrets = {
        "web": {
            "client_id": st.secrets["oauth"]["client_id"],
            "project_id": st.secrets["oauth"]["project_id"],
            "auth_uri": st.secrets["oauth"]["auth_uri"],
            "token_uri": st.secrets["oauth"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["oauth"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["oauth"]["client_secret"],
            "redirect_uris": st.secrets["oauth"]["redirect_uris"],
            "javascript_origins": st.secrets["oauth"]["javascript_origins"]
        }
    }

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_secrets,
        scopes=["https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/spreadsheets"]
    )
    flow.redirect_uri = st.secrets["google_redirect_uri"]
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"[Sign in with Google]({auth_url})", unsafe_allow_html=True)

    return flow