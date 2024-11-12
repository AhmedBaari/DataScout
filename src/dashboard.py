import googleapiclient
import streamlit as st
import pandas as pd
import requests
import concurrent.futures
from google_sheet_handling.google_auth import authenticate_with_google
from google_sheet_handling.google_sheets import list_google_sheets, load_sheet_data
from util.rate_limiter import RateLimiter
from util.processing import process_row

def main():
    st.title("DataScout")
    st.write("Welcome to DataScout!")
    st.write("Would you like to search a Google Sheet or upload a CSV file?")
    
    search_option = st.radio("Select an option", ("Search Google Sheet", "Upload CSV file"))
    upload_type = None
    
    if search_option == "Search Google Sheet":
        upload_type = "google"
    elif search_option == "Upload CSV file":
        upload_type = "csv"
    
    limiter = RateLimiter(max_requests=90, interval=60)
    
    if upload_type == "google":
        if 'credentials' not in st.session_state:
            flow = authenticate_with_google()
            auth_code = st.query_params.get("code", False)
            if auth_code:
                flow.fetch_token(code=auth_code)
                st.session_state['credentials'] = flow.credentials
        
        credentials = st.session_state.get('credentials')
        
        if credentials:
            sheets = list_google_sheets(credentials)
            sheet_names = [sheet['name'] for sheet in sheets]
            sheet_ids = {sheet['name']: sheet['id'] for sheet in sheets}
            selected_sheet = st.selectbox("Select a Google Sheet", sheet_names)
            
            if selected_sheet:
                sheet_id = sheet_ids[selected_sheet]
                try:
                    df = load_sheet_data(sheet_id, credentials)
                    st.session_state['df'] = df
                except googleapiclient.errors.HttpError as e:
                    st.error(f"An error occurred while loading the sheet data: {e}")
    
    elif upload_type == "csv":
        csv_file = st.file_uploader("Upload CSV file", type="csv")
        if csv_file:
            df = pd.read_csv(csv_file)
            st.session_state['df'] = df
    
    if 'df' in st.session_state:
        df = st.session_state['df']
        st.write(df.head())
        column = st.selectbox("Select a column", df.columns)
        st.write(df[column])
        
        search_prompt = st.text_input("Search (The column is placed as a placeholder below.)", value=f"{{{column}}}")
        if search_prompt and st.button("Search"):
            response = requests.post(
                "http://localhost:5000/makequery",
                json={"task": search_prompt, "column_name": column}
            )
            st.markdown("Searching with prompt: **`" + response.json().get("search_query").strip() + "`**")
            search_prompt = response.json()["search_query"]
            if "search_result" not in df.columns:
                df["search_result"] = ""
            if "llm_result" not in df.columns:
                df["llm_result"] = ""
            placeholder = st.empty()
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(process_row, index, row, search_prompt, df, limiter, placeholder) for index, row in df.iterrows()]
                concurrent.futures.wait(futures)
            st.write("Final Results:")
            st.write(df)

if __name__ == "__main__":
    main()