from .llm_integration import gemini_call
from .groqLLM import groq_call

def make_search_query(task,column_name):
    text = "You are an expert in search query optimization. Your task is to generate precise and targeted Google search queries, designed to retrieve specific information required by the task description. Ensure each search query is directly relevant to the specified data types, without including additional terms.\nTask Description: '{task}'\nColumn of Interest: {column_name}\nIf multiple query types are mentioned in the task description (such as 'phone number' and 'email'), generate only one search query for each type specified, separated by a comma. Avoid adding extra terms or synonyms, and do not generalize the query beyond each specific type. Maintain {{placeholders}} as they are in the response.\nReturn only the generated search queries, formatted for data entry purposes."





    print(text)
    #return gemini_call(text.format(task=task,column_name=column_name),candidate_count=1,temperature=0.2)
    return groq_call(text.format(task=task,column_name=column_name))
