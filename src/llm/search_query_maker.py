from .llm_integration import gemini_call

def make_search_query(task,column_name):
    text = "You are a search engine expert. Create an effective google search prompt to retrieve a corpus of results related to the task. Ensure the search query is relevant and flexible, capturing a broad scope to maximize useful information without being overly restrictive. Task: {task}. Column: {{{column_name}}}. Return only the search query for data entry purposes. Do not use quotes. Maintain {{placeholders}} as they are."

    print(text)
    return gemini_call(text.format(task=task,column_name=column_name),candidate_count=1,temperature=0.8)