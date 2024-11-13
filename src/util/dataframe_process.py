
import streamlit as st
import requests
import threading


def process_row(index, row, search_prompt, df, target_column, limiter, placeholder):
    row_json = row.to_dict()
    while not limiter.is_allowed():
        pass
    try:
        response = requests.post(
            "http://localhost:5000/search",
            json={"search_query": search_prompt, "row_data": row_json, "index": index}
        )
        response.raise_for_status()
        response_json = response.json()
        df.at[response_json["index"], target_column] = response_json["llm_result"]
        placeholder.dataframe(df)
    except requests.exceptions.RequestException as e:
        st.write(f"Error processing row {index}: {e}")
    except (KeyError, ValueError) as e:
        st.write(f"Error processing row {index}: Invalid response format")
    except Exception as e:
        st.write(f"Error processing row {index}: {e}")