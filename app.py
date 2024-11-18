from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from database import *
from models import *
from services import *
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jpdfter-rocks'  # Change this!
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx','txt'}

# Initialize tables in the database
with app.app_context():
    Base.metadata.create_all(bind=engine)

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
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Process the file
            processor = FileProcessorService()
            processed_content = processor.process_file(filepath)

            # Initialize ChatGPT API and process content
            chatgpt = ChatGPTAPI()
            notebook_content = chatgpt.process_document(processed_content)

            # Save to database
            db = next(get_db())
            new_notebook = Notebook(
                topic=filename,
                content=notebook_content,
                user_id=current_user.id  # Assuming you're using flask-login
            )
            db.add(new_notebook)
            db.commit()

            return jsonify({
                'message': 'File processed successfully',
                'notebook_id': new_notebook.id
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/notebooks', methods=['GET'])
@login_required
def get_notebooks():
    db = next(get_db())
    notebooks = db.query(Notebook).filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': notebook.id,
        'topic': notebook.topic,
        'content': notebook.content
    } for notebook in notebooks])

@login_manager.user_loader
def load_user(user_id):
    db = next(get_db())
    return db.query(User).get(int(user_id))

login_manager.login_view = 'login'  # Specify which route handles login

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = next(get_db())
    user = db.query(User).filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})
    
    return jsonify({'error': 'Invalid username or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)

