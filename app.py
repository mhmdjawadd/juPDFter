from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from database import *
from models import *
from services import *
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jpdfter-rocks'  # Change this!
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx','txt'}

# Initialize tables in the database
with app.app_context():
    Base.metadata.create_all(bind=engine)

api_key='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'
# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with get_db_context() as db:
        return db.query(User).get(int(user_id))


# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No file part'
        }), 400
    

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Process the file
            processor = FileProcessorService()
            processed_content = processor.process_file(filepath)

            # Initialize ChatGPT API and process content
            with get_db_context() as db:
                chatgpt = ChatGPTAPIService(api_key,current_user.id,db)
                response = chatgpt.process_text_and_create_notebooks(processed_content)
                 # Simply pass through the status and message from ChatGPTAPIService
                return jsonify(response), 200 if response['status'] == 'success' else jsonify(response), 500


        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({
        'status': 'error',
        'message': 'File type not allowed'
    }), 400

@app.route('/notebooks', methods=['GET'])
@login_required
def get_notebooks():
    try:
        with get_db_context() as db:
            notebooks = NotebookService.get_notebooks(db, current_user.id)
            return jsonify({
                'status': 'success',
                'message': 'Notebooks retrieved successfully',
                'data': [{
                    'id': notebook.id,
                    'topic': notebook.topic,
                    'content': notebook.content
                } for notebook in notebooks]
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve notebooks: {str(e)}'
        }), 500


login_manager.login_view = 'login'  # Specify which route handles login

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing username or password'
            }), 400
        with get_db_context() as db:
            user = db.query(User).filter_by(username=data['username']).first()
            
            if user and check_password_hash(user.password, data['password']):
                login_user(user)
                return jsonify({
                    'status': 'success',
                    'message': 'Logged in successfully'
                })
    
        return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        # Check if all required fields are present
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        username = data['username']
        email = data['email']
        password = data['password']

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email format'
            }), 400

        # Check if username or email already exists
        with get_db_context() as db:
            existing_user = db.query(User).filter(
                or_(User.username == username, User.email == email)
            ).first()
            
            if existing_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Username or email already exists'
                }), 400

            # Create new user
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password
            )
            
            db.add(new_user)
            db.commit()

        return jsonify({
            'status': 'success',
            'message': 'User registered successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500



@app.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Logout failed: {str(e)}'
        }), 500
if __name__ == '__main__':
    app.run(debug=True)

