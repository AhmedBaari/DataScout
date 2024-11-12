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
    response = tavily_client.search(prompt,include_raw_content=True,max_results=30)

    result_contents = ""
    for result in response["results"]:
        result_contents += result["content"]

    return result_contents
