from src.llm.llm_integration import gemini_call

def test_llm_integration():
    # Create prompts
    prompts = [
        "What is the capital of France?",
        "What is the capital of Germany?",
        "What is the capital of Italy?",
    ]


    for prompt in prompts:
        response = gemini_call(prompt)
        print(response.candidates[0].content.parts[0].text)


test_llm_integration()