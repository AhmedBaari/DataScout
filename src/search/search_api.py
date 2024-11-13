from tavily import TavilyClient
import os

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

# Instantiating TavilyClient
tavily_client = TavilyClient(api_key=api_key)

# Executing query
# Example: "Linkedin URL of Ahmed Baari"
def execute_query(prompt):
    try:
        response = tavily_client.search(prompt, include_raw_content=True, max_results=10, search_depth='advanced', include_answer=True)

        result_contents = ""
        result_contents += response["answer"]
        for result in response["results"]:
            result_contents += result["content"]

        return result_contents
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None