import googleapiclient
import requests
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
    
    # Ask user to choose a sheet in the file
    sheet_metadata = sheet.get(spreadsheetId=sheet_id).execute()
    sheets = sheet_metadata.get('sheets', [])
    sheet_names = [sheet['properties']['title'] for sheet in sheets]
    selected_sheet = st.selectbox("Select a sheet", sheet_names)
    
    # Load data from selected sheet
    result = sheet.values().get(spreadsheetId=sheet_id, range=selected_sheet).execute()
    data = result.get('values', [])
    df = pd.DataFrame(data[1:], columns=data[0])  # Convert to DataFrame
    
    # Check for duplicate column names
    if df.columns.duplicated().any():
        # Handle duplicate column names
        df = df.loc[:, ~df.columns.duplicated()]

    # Check if the number of columns in the loaded sheet matches the number of columns in the DataFrame
    if len(df.columns) != len(data[0]):
        # Handle the error by selecting only the columns that match the loaded sheet
        df = df.iloc[:, :len(data[0])]
    return df

def main():
    st.title("Dashboard")
    st.write("Welcome to the dashboard!")
    
    # Authenticate and get credentials
    if 'credentials' not in st.session_state:
        flow = authenticate_with_google()
        auth_code = st.query_params.get("code",False)
        st.write(st.query_params)
        
        if auth_code:
            flow.fetch_token(code=auth_code)
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
        # Create search query 
        response = requests.post(
            "http://localhost:5000/makequery",
            json={"task": search_prompt, "column_name": column}
        )
        st.write(response.json())

        st.write("Searching...")
        search_prompt = response.json()["search_query"]

        # Initialize columns for search and LLM results if not exist
        if "search_result" not in df.columns:
            df["search_result"] = ""
        if "llm_result" not in df.columns:
            df["llm_result"] = ""

        placeholder = st.empty()
        # Iterate over each row and make API call for each row
        for index, row in df.iterrows():

            row_json = row.to_dict()  # Convert row to dict to send as JSON
            response = requests.post(
                "http://localhost:5000/search",
                json={
                    "search_query": search_prompt,
                    "row_data": row_json,
                    "index": index
                }
            )

            # Update DataFrame with response data
            if response.status_code == 200:
                response_json = response.json()
                df.at[response_json["index"], "search_result"] = response_json["search_result"]
                df.at[response_json["index"], "llm_result"] = response_json["llm_result"]
                placeholder.dataframe(df)
            else:
                st.write(f"Error processing row {index}: API call failed")

        # Display the final DataFrame with all results
        st.write("Final Results:")
        st.write(df)

if __name__ == "__main__":
    main()