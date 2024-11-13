import base64
import streamlit as st
import pandas as pd
import requests
import concurrent.futures
from google_sheet_handling.auth import authenticate_with_google
from google_sheet_handling.google_sheets import list_google_sheets, load_sheet_data, write_dataframe_to_sheet
from util.rate_limits import RateLimiter
from util.dataframe_process import process_row
from llm import geminiLLM, query_optimization, groqLLM
from search import search_api


def make_query(task, column_name):
    """
    Function to create a refined search query.
    """
    try:
        # Generate search query
        search_query = query_optimization.make_search_query(task, column_name)
        # Extract multiple fields from the task
        fields = [field.strip() for field in task.split("and")]
        return {"search_query": search_query, "fields": fields}
    except Exception as e:
        st.error(f"Error generating query: {str(e)}")
        return None


def execute_search(search_query, row_data, fields):
    """
    Function to process search query with LLM.
    """
    try:
        # Convert row_data to DataFrame for ease of processing
        df = pd.DataFrame([row_data])
        # Modify search query with placeholders replaced by actual row data
        modified_query = search_query
        for column_name, value in row_data.items():
            placeholder = "{" + str(column_name) + "}"
            if placeholder in modified_query:
                modified_query = modified_query.replace(placeholder, str(value))

        search_result = search_api.execute_query(modified_query)
        prompt = f"Extract the information accurately. Task: {modified_query}\nResult: {search_result}\nReturn the exact value without additional words, explanations, or qualifiers. If the information is not present, return 'NOT AVAILABLE'. Format strictly for data entry."
        
        # Use the LLM to refine the search result
        llm_result = geminiLLM.gemini_call(prompt)
        
        return {
            "search_result": search_result,
            "llm_result": llm_result,
            "fields": fields
        }
    except Exception as e:
        st.error(f"Error during search execution: {str(e)}")
        return None


def main():
    st.title("DataScout")
    st.write("Welcome to DataScout! This tool searches the internet for information based on the data you provide, and writes the results back to your Google Sheet/csv file.")
    st.image('DataScoutBanner.png') 
    st.write("## Let's Load Your Data!")
    st.write("### Would you like to search a Google Sheet or upload a CSV file?")
    
    search_option = st.radio("**Select an option**", ("Search Google Sheet", "Upload CSV file"))
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
            selected_sheet = st.selectbox("Select a Google Sheet from your Google Drive:", sorted(list(sheet_options.keys())))
            
            if selected_sheet:
                try:
                    df, inner_sheet = load_sheet_data(sheet_options[selected_sheet], credentials)
                    st.session_state['sheet_df'] = df
                except Exception as e:
                    st.error(f"Error loading sheet data: {e}")
    
    # CSV Upload and Data Display
    elif upload_type == "csv":
        csv_file = st.file_uploader("Upload CSV file", type="csv")
        if csv_file:
            st.session_state['df'] = pd.read_csv(csv_file)
    
    # Data Search and Processing
    if 'df' in st.session_state or 'sheet_df' in st.session_state:
        df = st.session_state['df'] if 'df' in st.session_state else st.session_state['sheet_df']
        st.write("Here's a preview of your data:")
        st.write(df.head())
        st.write(f"## Let's Create The Search Query!")
        st.write("""### Instructions: \n- Select the column you want to search from the dropdown menu. \n- Enter a search prompt in the text box. \n- Click the `Refine` button to create a **refined web search prompt**. \n- Click the `Search` button to start the search using the refined prompt.""")
        column = st.selectbox("Select a column to search", df.columns)
        
        st.write(f"> *Example Search Prompt:* Get the email address and phone number for {{`{column}`}}")
        
        # User prompt input
        search_prompt = st.text_input("Enter search prompt", value=f"{{{column}}}")
        if search_prompt:
            if st.button("Create a **Refined Web Search Query**"):
                query_response = make_query(search_prompt, column)
                if query_response:
                    search_query = query_response.get("search_query", search_prompt)
                    st.markdown(f"#### Refined search query: \n**`{search_query.strip()}`**\n- Multiple search queries can be separated by commas.\n- Hit the refine button again to create another refined search query.\n- Click the search button to start the search with this query.")
                    st.session_state['search_query'] = search_query
                    st.session_state['fields'] = query_response.get("fields")
                    st.session_state['refine_status'] = True
        
        # Search execution
        if st.session_state.get('refine_status') and st.button("**Scout the Internet!**"):
            st.session_state['search'] = True
            st.session_state['search_complete'] = False
        if st.session_state.get('search_query', False) and st.session_state.get('search', False) and st.session_state.get('search_complete', False) == False:
            st.write("### Searching the internet for information...")
            st.write("*Refining your results may take a while...*")
            queries = st.session_state.get('search_query', False).split(",")
            
            # Parallel processing of search queries
            for i, query in enumerate(queries, start=1):
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [
                        executor.submit(process_row, idx, row, query.strip(), df, f"search_result_{i}", limiter, st.empty()) 
                        for idx, row in df.iterrows()
                    ]
                    concurrent.futures.wait(futures)
            
            st.session_state['search_complete'] = True
            st.session_state['df'] = df

        if st.session_state.get('search_complete', False):
            st.write("### Result")
            st.write(st.session_state.get('df'))
            
            st.write("#### Let's Export The Data\nHow would you like to export the data?")
            
            # Download CSV file
            if st.button("Download as CSV", key="download_button"):
                csv_data = st.session_state.get('df').to_csv(index=False)
                b64 = base64.b64encode(csv_data.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)

            # Write results to Google Sheet
            if st.button("Export back to Google Sheet", key="write_button"):
                if 'credentials' in st.session_state:
                    credentials = st.session_state.get('credentials')
                    result = write_dataframe_to_sheet(st.session_state.get('df'), sheet_options[selected_sheet], inner_sheet, credentials)
                    st.write("Data written to Google Sheet successfully!")
                else:
                    st.error("No Google Sheet credentials found. Please authenticate with Google first.")


if __name__ == "__main__":
    main()
