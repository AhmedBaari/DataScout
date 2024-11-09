from flask import Flask, request, jsonify
import pandas as pd
import json
from llm import llm_integration
from search import search_api

app = Flask(__name__)

# For Development Purposes
# app.debug = True
# app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def hello():
    return {"message": "Hello, World!", "status": 200}


@app.route('/search', methods=['POST'])
def search():
    try:
        # Parse request JSON
        data = request.get_json()
        
        search_query = data.get("search_query")
        dataframe_json = json.loads(data.get("dataframe"))
        
        
        # Convert JSON to DataFrame
        df = pd.DataFrame(dataframe_json)#.T
        print("DATAFRAME: ", df)

        target_column = df.columns[0]
 
        # PROCESSING -- TODO
        print(df)

        # Create a new column with the search prompt
        # Iterate over each row in the dataframe
        for index, row in df.iterrows():
            # Create a new column with the search prompt
            # Iterate over each row in the dataframe
            for index, row in df.iterrows():
                modified_query = search_query
                # Replace placeholders with values from the row
                for column_name in df.columns:
                    placeholder = "{" + str(column_name) + "}"
                    if placeholder in modified_query:
                        modified_query = modified_query.replace(placeholder, str(row[column_name]))
                # Assign the modified query to the search_prompt column
                df.at[index, "search_prompt"] = modified_query
            # Assign the modified query to the search_prompt column
            df.at[index, "search_prompt"] = modified_query


        # Get value using LLM
        # Get value using LLM
        #df["llm_result"] = df["search_prompt"].apply(llm_integration.gemini_call)

        # Get value using search
        df["search_result"] =  df["search_prompt"].apply(search_api.execute_query)
        df["llm_result"] = ""
        
        # iterate through each row
        for index, row in df.iterrows():
            search_prompt = row["search_prompt"]
            search_result = row["search_result"]

            prompt = """Task: {search_prompt}\nResult: {search_result}\nRETURN THE EXACT VALUE ONLY""".format(search_prompt=search_prompt, search_result=search_result)

            df.at[index, "llm_result"] = llm_integration.gemini_call(prompt)

        # Stream the response
        result_json = df.to_json(orient="columns")
        response = app.response_class(
            response=result_json,
            status=200,
            mimetype='application/json',
            direct_passthrough=True
        )
        response.headers['Content-Disposition'] = 'attachment; filename=result.json'
        return response

    except Exception as e:
        print("ERROR: ",e)
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(port=5000)  
