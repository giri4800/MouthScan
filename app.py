import os
import logging
from flask import Flask, render_template, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    try:
        # Configuration
        app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "dev_key")
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
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
            # Import models here to avoid circular imports
            from models import User, Analysis
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
    from models import User
    return User.query.get(int(user_id))

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    analyses = None
    if current_user.is_authenticated:
        analyses = current_user.analyses
    return render_template('dashboard.html', analyses=analyses)

@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file:
        try:
            # Save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(filepath)
            
            # Analyze the image
            from utils.ai_analyzer import AIAnalyzer
            analyzer = AIAnalyzer()
            result, confidence = analyzer.analyze_image(filepath)
            
            # Create analysis record
            analysis = Analysis(
                user_id=current_user.id,
                image_path=filepath,
                result=result,
                confidence=confidence,
                status='completed'
            )
            db.session.add(analysis)
            db.session.commit()
            
            logger.info(f"Analysis completed for user {current_user.id}: {result} ({confidence:.2%})")
            return jsonify({'analysis_id': analysis.id}), 200
            
        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            return jsonify({'error': 'Failed to process image'}), 500
    
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/analysis/<int:id>')
@login_required
def analysis(id):
    analysis = Analysis.query.get_or_404(id)
    if analysis.user_id != current_user.id:
        abort(403)
    return render_template('analysis.html', analysis=analysis)
