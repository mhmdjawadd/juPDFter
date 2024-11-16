from flask import Flask, request, jsonify
from models.base import Base
from models.notebook import Notebook
from services.file_processor import process_file
from services.api_layer import APILayer
from services.notebook_api_layer import NotebookAPILayer
from database import engine, Session

app = Flask(__name__)

@app.route('/process-document', methods=['POST'])
def process_document():
    try:
        file = request.files['document']
        if not file:
            return jsonify({'error': 'No document provided'}), 400

        session = Session()
        
        # Process the file using your existing processor
        processed_text = process_file(file)
        
        # Get topics from initial API layer
        api_layer = APILayer()
        topics = api_layer.get_topics(processed_text)

        # Generate notebooks for each topic
        notebook_layer = NotebookAPILayer()
        notebooks = []
        for topic in topics:
            notebook_content = notebook_layer.generate_notebook(topic, processed_text)
            notebook = Notebook(
                topic=topic,
                content=notebook_content
            )
            session.add(notebook)
            notebooks.append(notebook)
        
        session.commit()
        
        return jsonify({
            'topics': topics,
            'notebook_count': len(notebooks)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
