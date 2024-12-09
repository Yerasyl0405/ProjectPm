from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai

load_dotenv()

# Получение API-ключа из переменных окружения
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Конфигурация модели
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are a therapist who helps people with mental health issues.\n",
)

