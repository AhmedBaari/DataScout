from flask import Flask

app = Flask(__name__)

# For Development Purposes
# app.debug = True
# app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def hello():
    return {"message": "Hello, World!", "status": 200}

if __name__ == "__main__":
    app.run(port=5000)  
