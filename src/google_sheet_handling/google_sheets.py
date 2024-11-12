from googleapiclient.discovery import build
import pandas as pd
import streamlit as st

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
    
    sheet_metadata = sheet.get(spreadsheetId=sheet_id).execute()
    sheets = sheet_metadata.get('sheets', [])
    sheet_names = [sheet['properties']['title'] for sheet in sheets]
    selected_sheet = st.selectbox("Select a sheet", sheet_names)
    
    result = sheet.values().get(spreadsheetId=sheet_id, range=selected_sheet).execute()
    data = result.get('values', [])
    df = pd.DataFrame(data[1:], columns=data[0])
    
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]

    if len(df.columns) != len(data[0]):
        df = df.iloc[:, :len(data[0])]
    return df