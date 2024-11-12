from flask import Flask, request, jsonify
import pandas as pd
import json
from llm import llm_integration, search_query_maker, groqLLM
from search import search_api

app = Flask(__name__)

# For Development Purposes
#app.debug = True
#app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def hello():
    return {"message": "Hello, World!", "status": 200}

@app.route('/makequery', methods=['POST'])
def makequery():
    try:
        # Parse request JSON
        data = request.get_json()
        task = data.get("task")
        column_name = data.get("column_name")
        print(task, column_name)

        # Generate search query
        search_query = search_query_maker.make_search_query(task, column_name)

        # Extract multiple fields from the task
        fields = [field.strip() for field in task.split("and")]

        print("GENERATED QUERY: ", search_query)
        return jsonify({"search_query": search_query, "fields": fields}), 200

    except Exception as e:
        print("ERROR: ", e)
        return jsonify({"error": str(e)}), 400

@app.route('/search', methods=['POST'])
def search():
    try:
        # Parse request JSON
        data = request.get_json()
        search_query = data.get("search_query")
        row_data = data.get("row_data")  # Single row data
        fields = data.get("fields")  # Multiple fields

        # Convert row_data to DataFrame for ease of processing
        df = pd.DataFrame([row_data])

        # Create the search prompt by replacing placeholders in the search_query
        modified_query = search_query
        for column_name, value in row_data.items():
            placeholder = "{" + str(column_name) + "}"
            if placeholder in modified_query:
                modified_query = modified_query.replace(placeholder, str(value))

        print("SEARCHING: ", modified_query)
        # Perform search and LLM processing
        search_result = search_api.execute_query(modified_query)
        prompt = f"Extract the information accurately. Task: {modified_query}\nResult: {search_result}\nReturn the exact value without additional words, explanations, or qualifiers. If the information is not present, return 'NOT AVAILABLE'. Format strictly for data entry."
        
        print("REFINING: ", modified_query, " --- \n",search_result)
        llm_result = llm_integration.gemini_call(prompt)
        #llm_result = groqLLM.groq_call(prompt)

        # Prepare response JSON for single row
        result = {
            "index": data.get("index"),  # Ensure to send back the row index for updating in dashboard
            "search_result": search_result,
            "llm_result": llm_result,
            "fields": fields
        }
        
        return jsonify(result), 200

    except Exception as e:
        print("ERROR: ", e)
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(port=5000)  