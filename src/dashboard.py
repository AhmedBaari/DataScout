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

            # Perform API Call
            response = requests.get("http://localhost:5000")
            if response.status_code == 200:
                st.write(response.json())
            else:
                st.write("Error: API Call failed")

if __name__ == "__main__":
    dashboard()