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
from pathlib import Path
import nbformat

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jpdfter-rocks'  # Change this!
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx','txt'}

# Initialize tables in the database
with app.app_context():
    print("Initializing database from app.py")
    init_db()

api_key=""
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
def upload_file_and_create_notebooks():
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
            processed_content = processor.process_file(file)

            # Initialize ChatGPT API and process content
            with get_db_context() as db:
                chatgpt = ChatGPTAPIService(api_key,current_user.id,db)
                response = chatgpt.process_text_and_create_notebooks(processed_content)
                 # Simply pass through the status and message from ChatGPTAPIService
                if response['status'] == 'success':
                    return jsonify(response), 200 
                else:
                    return jsonify(response), 500

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Failed to process file: {str(e)}'
            }), 500
        finally:
            pass

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
                }),200

    
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
        print(f"Registration failed: {str(e)}")
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

@app.route('/download-notebooks', methods=['GET'])
@login_required
def download_notebooks():
    try:
        with get_db_context() as db:
            # Get current user's notebooks
            notebooks = NotebookService.get_notebooks(db, current_user.id)
            
            if not notebooks:
                return jsonify({
                    'status': 'error',
                    'message': 'No notebooks found'
                }), 404

            # Create downloads directory
            downloads_path = Path.home() / 'Downloads' / 'juPDFter_notebooks'
            downloads_path.mkdir(parents=True, exist_ok=True)

            saved_files = []
            for notebook in notebooks:
                try:
                    # Create a new notebook using nbformat
                    nb = nbformat.v4.new_notebook()
                    
                    # Convert the content string to markdown cells
                    # Split content by newlines to create separate cells
                    content_lines = notebook.content.split('\n')
                    cells = []
                    
                    current_cell = []
                    for line in content_lines:
                        if line.startswith('#'):  # New section starts
                            if current_cell:  # Save previous cell if exists
                                cells.append(nbformat.v4.new_markdown_cell('\n'.join(current_cell)))
                                current_cell = []
                        current_cell.append(line)
                    
                    # Add the last cell if exists
                    if current_cell:
                        cells.append(nbformat.v4.new_markdown_cell('\n'.join(current_cell)))
                    
                    nb['cells'] = cells

                    # Save notebook
                    notebook_path = downloads_path / notebook.topic
                    with open(notebook_path, 'w', encoding='utf-8') as f:
                        nbformat.write(nb, f)
                    
                    saved_files.append(notebook.topic)
                
                except Exception as e:
                    print(f"Error processing notebook {notebook.topic}: {str(e)}")
                    continue

            if not saved_files:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to save any notebooks'
                }), 500

            return jsonify({
                'status': 'success',
                'message': 'Notebooks downloaded successfully',
                'saved_files': saved_files,
                'download_path': str(downloads_path)
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to download notebooks: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

