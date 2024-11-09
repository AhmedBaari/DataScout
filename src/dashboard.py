import streamlit as st
import pandas as pd
import requests

def dashboard():
    st.title("Dashboard")
    st.write("Welcome to the dashboard!")

    # Input CSV file
    csv_file = st.file_uploader("Upload CSV file", type="csv")
    if csv_file is not None:
        df = pd.read_csv(csv_file)
        st.write(df)

        # Select a column
        if df is not None:
            column = st.selectbox("Select a column", df.columns)
            st.write(df[column])

        # Create a search prompt
        # Column name as placeholder value
        search_prompt = st.text_input("Search", value=f"{{{column}}}")

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
    dashboard()