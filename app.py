from flask import Flask, request, jsonify
import datetime
from functools import wraps
from database import *
from models import *
from services import *
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path
import nbformat
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jpdfter-rocks'  # Change this!
api_key = 'your-api-key'  # Set your API key here

# Initialize tables in the database
with app.app_context():
    print("Initializing database from app.py")
    init_db(reset=True)

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # JWT is expected in the Authorization header
        auth_header = request.headers.get('Authorization', None)
        if auth_header:
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token to get the user info
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            with get_db_context() as db:
                current_user = db.query(User).filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# User registration route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    hashed_password = generate_password_hash(password)
    with get_db_context() as db:
        new_user = User(username=username, password=hashed_password)
        db.add(new_user)
        db.commit()

    return jsonify({'message': 'Registered successfully'}), 201

# User login route
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    username = auth.get('username')
    password = auth.get('password')

    if not username or not password:
        return jsonify({
    'status': 'error',
    'message': 'Could not verify'
}), 401


    with get_db_context() as db:
        user = db.query(User).filter_by(username=username).first()

    if not user:
        return jsonify({
    'status': 'error',
    'message': 'User not found'
}), 401

    if check_password_hash(user.password, password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({
    'status': 'error',
    'message': 'Could not verify'
}), 401

# File upload and notebook creation route
@app.route('/upload', methods=['POST'])
@token_required
def upload_file_and_create_notebooks(current_user):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    try:
        # Process the file directly
        processor = FileProcessorService()
        processed_content = processor.process_file(file)

        # Initialize ChatGPT API and process content
        with get_db_context() as db:
            chatgpt = ChatGPTAPIService(api_key, current_user.id, db)
            response = chatgpt.process_text_and_create_notebooks(processed_content)

            if response['status'] == 'success':
                return jsonify(response), 200
            else:
                return jsonify(response), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to process file: {str(e)}'}), 500

# Route to get notebooks
@app.route('/notebooks', methods=['GET'])
@token_required
def get_notebooks(current_user):
    try:
        with get_db_context() as db:
            notebooks = NotebookService.get_notebooks(db, current_user.id)
            notebook_data = [
                {'id': nb.id, 'topic': nb.topic, 'content': nb.content} for nb in notebooks
            ]
            return jsonify({
                'status': 'success',
                'message': 'Notebooks retrieved successfully',
                'data': notebook_data
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to retrieve notebooks: {str(e)}'}), 500

# Route to download notebooks
@app.route('/download-notebooks', methods=['GET'])
@token_required
def download_notebooks(current_user):
    try:
        with get_db_context() as db:
            notebooks = NotebookService.get_notebooks(db, current_user.id)

            if not notebooks:
                return jsonify({'status': 'error', 'message': 'No notebooks found'}), 404

            downloads_path = Path.home() / 'Downloads' / 'juPDFter_notebooks'
            downloads_path.mkdir(parents=True, exist_ok=True)

            saved_files = []
            for notebook in notebooks:
                try:
                    # Create a new notebook using nbformat
                    nb = nbformat.v4.new_notebook()

                    # Convert the content string to markdown cells
                    content_lines = notebook.content.split('\n')
                    cells = []
                    current_cell = []

                    for line in content_lines:
                        if line.startswith('#'):
                            if current_cell:
                                cells.append(nbformat.v4.new_markdown_cell('\n'.join(current_cell)))
                                current_cell = []
                        current_cell.append(line)

                    if current_cell:
                        cells.append(nbformat.v4.new_markdown_cell('\n'.join(current_cell)))

                    nb['cells'] = cells

                    # Save notebook
                    notebook_filename = f"{notebook.topic}.ipynb"
                    notebook_path = downloads_path / notebook_filename
                    with open(notebook_path, 'w', encoding='utf-8') as f:
                        nbformat.write(nb, f)

                    saved_files.append(notebook_filename)

                except Exception as e:
                    print(f"Error processing notebook {notebook.topic}: {str(e)}")
                    continue

            if not saved_files:
                return jsonify({'status': 'error', 'message': 'Failed to save any notebooks'}), 500

            return jsonify({
                'status': 'success',
                'message': 'Notebooks downloaded successfully',
                'saved_files': saved_files,
                'download_path': str(downloads_path)
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to download notebooks: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)