import base64
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
    st.write("Choose to search a Google Sheet or upload a CSV file:")
    
    search_option = st.radio("Select an option", ("Search Google Sheet", "Upload CSV file"))
    upload_type = "google" if search_option == "Search Google Sheet" else "csv"
    limiter = RateLimiter(max_requests=3, interval=30)
    
    # Google Sheet selection and loading
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
            sheet_options = {sheet['name']: sheet['id'] for sheet in sheets}
            selected_sheet = st.selectbox("Select a Google Sheet", sorted(list(sheet_options.keys())))
            
            if selected_sheet:
                try:
                    df,inner_sheet = load_sheet_data(sheet_options[selected_sheet], credentials)
                    #st.dataframe(df)
                    st.session_state['sheet_df'] = df
                except Exception as e:
                    st.error(f"Error loading sheet data: {e}")
    
    # CSV Upload and Data Display
    elif upload_type == "csv":
        csv_file = st.file_uploader("Upload CSV file", type="csv")
        if csv_file:
            pass
            #st.session_state['df'] = pd.read_csv(csv_file)
    
    # Data Search and Processing
    if 'df' in st.session_state or 'sheet_df' in st.session_state:
        df = st.session_state['df'] if 'df' in st.session_state else st.session_state['sheet_df']
        st.write(df.head())
        column = st.selectbox("Select a column to search", df.columns)
        
        # User prompt input
        search_prompt = st.text_input("Enter search prompt", value=f"{{{column}}}")
        if search_prompt:
            st.session_state['refine_status'] = False
            if st.button("Refine"):
                response = requests.post("http://localhost:5000/makequery", json={"task": search_prompt, "column_name": column})
                search_query = response.json().get("search_query", search_prompt)
                st.markdown(f"Refined prompt: **`{search_query.strip()}`**")
                st.session_state['search_query'] = search_query
                st.session_state['refine_status'] = True
        
        # Search execution
        if st.button("Search"):
            st.session_state['search'] = True
            st.session_state['search_complete'] = False
        if st.session_state.get('search_query', False) and st.session_state.get('search', False) and st.session_state.get('search_complete', False) == False:
            queries = st.session_state.get('search_query', False).split(",")
            
            # Parallel processing of search queries
            for i, query in enumerate(queries, start=1):
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(process_row, idx, row, query.strip(), df, f"search_result_{i}", limiter, st.empty()) for idx, row in df.iterrows()]
                    concurrent.futures.wait(futures)
            

            st.session_state['search_complete'] = True
            st.session_state['df'] = df

        if st.session_state.get('search_complete', False):
            st.write("Final Results:")
            st.write(st.session_state.get('df'))
            

            st.write(df)

if __name__ == "__main__":
    main()
