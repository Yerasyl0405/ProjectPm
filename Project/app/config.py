import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://yerassyl:12345era@localhost:5432/PmProject'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
