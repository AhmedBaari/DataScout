import googleapiclient
import streamlit as st
import pandas as pd
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def authenticate_with_google():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=["https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    flow.redirect_uri = "http://localhost:8501"
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.write(f"[Sign in with Google]({auth_url})")

    return flow

def list_google_sheets(credentials):
    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        spaces='drive',
        fields="nextPageToken, files(id, name)").execute()
    sheets = results.get('files', [])
    return sheets

def load_sheet_data(sheet_id, credentials):
    sheets_service = build('sheets', 'v4', credentials=credentials)
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range="Sheet1").execute()
    data = result.get('values', [])
    df = pd.DataFrame(data[1:], columns=data[0])  # Convert to DataFrame
    return df

def main():
    st.title("Dashboard")
    st.write("Welcome to the dashboard!")
    
    # Authenticate and get credentials
    if 'credentials' not in st.session_state:
        flow = authenticate_with_google()
        auth_code = st.experimental_get_query_params().get("code")
        
        if auth_code:
            flow.fetch_token(code=auth_code[0])
            credentials = flow.credentials
            st.session_state['credentials'] = credentials
    
    credentials = st.session_state.get('credentials')
    
    # List sheets after authentication
    selected = False 
    if credentials:
        sheets = list_google_sheets(credentials)
        sheet_names = [sheet['name'] for sheet in sheets]
        sheet_ids = {sheet['name']: sheet['id'] for sheet in sheets}
        selected_sheet = st.selectbox("Select a Google Sheet", sheet_names)
        
        if selected_sheet:
            selected = True
            sheet_id = sheet_ids[selected_sheet]
            try:
                df = load_sheet_data(sheet_id, credentials)
            except googleapiclient.errors.HttpError as e:
                st.error(f"An error occurred while loading the sheet data: {e}")
            #st.write(df)

            
            # Display data preview
            #st.write("Preview of Google Sheet Data:")
            #st.write(df.head())
            



    # CSV upload option
    csv_file = st.file_uploader("Upload CSV file", type="csv")
    if csv_file:
        df = pd.read_csv(csv_file)

    if csv_file or selected:
        st.write(df.head())
        column = st.selectbox("Select a column", df.columns)
        st.write(df[column])

        # Create a search prompt
        # Column name as placeholder value
        search_prompt = st.text_input("Search (The column is placed as a placeholder below.)", value=f"{{{column}}}")

        # Button - Perform search operation
        if st.button("Search"):
            st.write("searching...")

            # Convert the dataframe column to JSON string
            json_data = df.loc[:,[column]].to_json(orient="records")

            # Perform API Call with streaming
            response = requests.post("http://localhost:5000/search", json={"search_query": search_prompt, "dataframe": json_data}, stream=True)
            if response.status_code == 200:
                response_json = response.json()
                df_result = pd.DataFrame(response_json)
                st.write(df_result)
            else:
                print(response.status_code)
                st.write("Error: API Call failed")

if __name__ == "__main__":
    main()