from flask import Flask, request, jsonify
import openai
import os

# Initialize the OpenAI API client with your API key
openai.api_key = 'org-Wwl6faZ3kRIRBobm9AhcdYS2'  # Replace with your OpenAI API key

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get('message')

    # Call the OpenAI API to get the response
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # You can choose other models like gpt-3.5-turbo
            prompt=user_message,
            max_tokens=150
        )
        chatbot_reply = response.choices[0].text.strip()
        return jsonify({"response": chatbot_reply})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
