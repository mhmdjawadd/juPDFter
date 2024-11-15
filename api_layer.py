from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import openai  
import PyPDF2  

# Initialize the Flask app and configure the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define a model (modify as needed)
class ChatRequest(db.Model):
    __tablename__ = 'chat_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_query = db.Column(db.String, nullable=False)
    response = db.Column(db.String, nullable=True)

# Route for handling requests to ChatGPT
@app.route('/api/chat', methods=['POST'])
def chat_with_gpt():
    data = request.get_json()
    user_query = data.get("query")
    pdf_file = data.get("pdf_file")  # Expecting a PDF file in the request

    if not user_query or not pdf_file:
        return jsonify({"error": "No query or PDF file provided"}), 400

    # Read the PDF file
    pdf_text = ""
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"
    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500

    # ChatGPT API interaction
    try:
        openai.api_key = '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'
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract every topic found in the following text:\n\n{pdf_text}\n\nUser Query: {user_query}"}
        ]
        chat_response = openai.ChatCompletion.create(
            model="gpt-4-turbo-128k",  # Using gpt-4-turbo
            messages=messages,
            max_tokens=100000  # Set to the maximum allowed tokens for gpt-4-turbo
        )

        response_text = chat_response['choices'][0]['message']['content'].strip()

        # Save the request and response in the database
        chat_request = ChatRequest(user_query=user_query, response=response_text)
        db.session.add(chat_request)
        db.session.commit()

        return jsonify({"response": response_text.splitlines()}), 200  # Return response as a list of strings

    except (SQLAlchemyError, Exception) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
