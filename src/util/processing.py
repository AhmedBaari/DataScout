
import streamlit as st
import requests


def process_row(index, row, search_prompt, df, limiter, placeholder):
    row_json = row.to_dict()
    while not limiter.is_allowed():
        pass
    response = requests.post(
        "http://localhost:5000/search",
        json={"search_query": search_prompt, "row_data": row_json, "index": index}
    )
    if response.status_code == 200:
        response_json = response.json()
        df.at[response_json["index"], "search_result"] = response_json["search_result"]
        df.at[response_json["index"], "llm_result"] = response_json["llm_result"]
        placeholder.dataframe(df)
    else:
        st.write(f"Error processing row {index}: API call failed")