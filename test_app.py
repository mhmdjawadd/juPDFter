from app import app
import pytest, json
from werkzeug.datastructures import FileStorage
from pathlib import Path

@pytest.fixture(scope='function')
def test_client():
    app.config['TESTING'] = True

    
    with app.test_client() as client:
        yield client
"""
def test_tables_exist():
    # Get the inspector
    inspector = inspect(engine)
    
    # Get all table names in the database
    existing_tables = inspector.get_table_names()
    print(existing_tables)
    # Define expected tables
    expected_tables = ['UserTable', 'NotebookTable']
    
    # Check if all expected tables exist
    for table in expected_tables:
        assert table in existing_tables, f"Table '{table}' not found in database"
    
    # Optional: Print table details for debugging
    for table_name in existing_tables:
        columns = inspector.get_columns(table_name)
        print(f"\nTable: {table_name}")
        for column in columns:
            print(f"- {column['name']}: {column['type']}")


@mark.timeout(1)
def test_signup(test_client):
    # Test successful signup
    response = test_client.post('/signup', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    if response.json['message'] != 'Username or email already exists':
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        print('successful signup in signup test')

    # Test duplicate username
    response = test_client.post('/signup', json={
        'username': 'testuser',
        'email': 'another@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 400
    assert response.json['status'] == 'error'


@mark.timeout(5)
def test_login(test_client):
    print('=== Starting login test ===', flush=True)
    
    test_username = f'logintest_1234'
    
    # Test signup
    signup_data = {
        'username': test_username,
        'email': f'{test_username}@example.com',
        'password': 'testpass123'
    }
    print(f'Attempting signup with: {signup_data}', flush=True)
    signup_response = test_client.post('/signup', json=signup_data)
    print(f'Signup response: {signup_response.json}', flush=True)
    print(f'Signup status code: {signup_response.status_code}', flush=True)
    assert signup_response.status_code == 201, f"Signup failed: {signup_response.json}"

    # Test login
    login_data = {
        'username': test_username,
        'password': 'testpass123'
    }
    print(f'Attempting login with: {login_data}', flush=True)
    login_response = test_client.post('/login', json=login_data)
    print(f'Login status code: {login_response.status_code}', flush=True)
    print(f'Login response: {login_response.json}', flush=True)
    print(f'Login status code: {login_response.status_code}', flush=True)
    assert login_response.status_code == 200, f"Login failed with status {login_response.status_code}: {login_response.json}"
"""

"""
def test_upload_file(test_client):
    
    response = test_client.post('/signup', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })

    login_response = test_client.post('/login', json={
        'username': 'uploadtest',
        'password': 'testpass123'
    })
    assert login_response.status_code == 200, "Login failed"

    with open('./tests/test.txt', 'rb') as f:
        file = FileStorage(
            stream=f,
            filename='test.txt',
            content_type='text/plain'

        )
        data = {'file': file}
        
        # Upload the file
        response = test_client.post('/upload', 
                                  data=data,
                                  content_type='multipart/form-data')
        
        print("Upload Response:", flush=True)
        print(f"Status Code: {response.status_code}", flush=True)
        print(f"Response Data: {response.json}", flush=True)
        
        # Check upload success
        assert response.status_code == 200, f"Upload failed: {response.json}"
        assert response.json['status'] == 'success'

        # Verify notebooks were created
        notebooks_response = test_client.get('/notebooks')
        assert notebooks_response.status_code == 200
        assert 'data' in notebooks_response.json
        assert len(notebooks_response.json['data']) > 0, "No notebooks were created"

"""
"""def test_get_notebooks(test_client):
    # First login
    test_client.post('/signup', json={
        'username': 'notebooktest1',
        'email': 'notebook@example.com',
        'password': 'testpass123'
    })
    test_client.post('/login', json={
        'username': 'notebooktest',
        'password': 'testpass123'
    })

    response = test_client.get('/notebooks')
    assert response.status_code == 200
    assert 'data' in response.json 

"""
def test_download_notebooks(test_client):
    # First login
    sign_up = test_client.post('/signup', json={
        'username': 'mohammadjawad',
        'email': 'download@example.com',
        'password': 'testpass123'
    })
    assert sign_up.status_code == 201, "Signup failed"
    login_response = test_client.post('/login', json={
        'username': 'mohammadjawad',
        'password': 'testpass123'
    })
    assert login_response.status_code == 200, "Login failed"

    # Upload a test file first to ensure we have notebooks
    with open('./tests/test.txt', 'rb') as f:
        file = FileStorage(
            stream=f,
            filename='test.txt',
            content_type='text/plain'

        )
        data = {'file': file}
        
        # Upload the file
    
        response = test_client.post('/upload', 
                                  data=data,
                                  content_type='multipart/form-data')
    

    # Test downloading notebooks
    download_response = test_client.get('/download-notebooks')
    assert download_response.status_code == 200, "Download failed"
    assert download_response.json['status'] == 'success'
    
    # Verify files were created in downloads folder
    downloads_path = Path.home() / 'Downloads' / 'juPDFter_notebooks'
    assert downloads_path.exists(), "Downloads folder was not created"
    
    # Check if notebooks were saved
    notebooks = list(downloads_path.glob('*.ipynb'))
    assert len(notebooks) > 0, "No notebooks were saved"
    
    # Verify notebook content
    for notebook_path in notebooks:
        assert notebook_path.stat().st_size > 0, f"Notebook {notebook_path} is empty"
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)
            assert isinstance(notebook_content, dict), "Invalid notebook format"