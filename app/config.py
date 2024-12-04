import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '4543ergdfg')
    SQLALCHEMY_DATABASE_URI = 'postgresql://pm_project_user:bQpkG3Be0mz48gOTMrcHCWyOJDKShCcL@dpg-ct88oqogph6c73d3tnpg-a.oregon-postgres.render.com/pm_project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  # Example for Gmail, adjust for your email provider
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'yeranura489@gmail.com'  # Your email
    MAIL_PASSWORD = 'bxof nbue qbrx qxuh'  # Your email password
    MAIL_DEFAULT_SENDER = 'yeranura489@gmail.com'  # Your email

