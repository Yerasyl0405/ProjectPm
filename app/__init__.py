from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app.config import Config
from flask_mail import Mail


db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max size for uploads

    db.init_app(app)
    bcrypt.init_app(app)


    with app.app_context():
        db.create_all()

    # Import and register blueprints inside the function
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.question import question_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(question_bp)


    mail = Mail(app)

    return app
