from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Укажите ваш OpenAI API-ключ
API_KEY = "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"

# Конечная точка OpenAI API
API_URL = "https://api.openai.com/v1/chat/completions"


@app.route('/')
def index():
    return render_template('index.html')  # HTML-файл для фронтенда


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    # Формируем запрос к OpenAI
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_input}],
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        ai_reply = response.json().get('choices', [])[0]['message']['content']
        return jsonify({"reply": ai_reply})
    else:
        return jsonify({"error": "Failed to connect to OpenAI", "details": response.json()}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)

