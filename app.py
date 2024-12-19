
import os
import logging
from flask import Flask, render_template, request, jsonify, abort
from flask_login import LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Analysis

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    try:
        # Configuration
        app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "dev_key")
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        
        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            
            # Register blueprints
            from auth import auth as auth_blueprint
            app.register_blueprint(auth_blueprint)
            logger.info("Application initialized successfully")
            
        return app
    except Exception as e:
        logger.error(f"Error creating app: {str(e)}")
        raise

app = create_app()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes remain the same...
