import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from routes.views import views_bp
from routes.api import api_bp
from auth import auth_bp
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/emergency_triage')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

app = create_app()

# Create tables with retry logic
with app.app_context():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db.create_all()
            print("Database tables created (if they didn't exist)")
            break
        except Exception as e:
            print(f"Database connection attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("Could not connect to database after multiple attempts.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)