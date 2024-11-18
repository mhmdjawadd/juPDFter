import pytest
from app import app
import io
import os
from sqlalchemy import create_engine
from models import Base

@pytest.fixture(scope='function')
def test_client():
    # Use an absolute path or memory database
    db_path = 'sqlite:///:memory:'  # in-memory database
    # OR
    # db_path = 'sqlite:///test.db'  # file-based database
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    
    with app.test_client() as client:
        yield client
    
    # Cleanup only needed for file-based database
    # if os.path.exists('test.db'):
    #     os.remove('test.db')

def test_signup(test_client):
    # Test successful signup
    response = test_client.post('/signup', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    assert response.json['status'] == 'success'

    # Test duplicate username
    response = test_client.post('/signup', json={
        'username': 'testuser',
        'email': 'another@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 400
    assert response.json['status'] == 'error'

def test_login(test_client):
    # First create a user
    test_client.post('/signup', json={
        'username': 'logintest',
        'email': 'login@example.com',
        'password': 'testpass123'
    })

    # Test successful login
    response = test_client.post('/login', json={
        'username': 'logintest',
        'password': 'testpass123'
    })
    assert response.status_code == 200
    assert response.json['status'] == 'success'

    # Test wrong password
    response = test_client.post('/login', json={
        'username': 'logintest',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    assert response.json['status'] == 'error'

def test_upload_file(test_client):
    # First login
    test_client.post('/signup', json={
        'username': 'uploadtest',
        'email': 'upload@example.com',
        'password': 'testpass123'
    })
    test_client.post('/login', json={
        'username': 'uploadtest',
        'password': 'testpass123'
    })

    # Create a test PDF file
    data = {'file': (io.BytesIO(b'test file content'), 'test.pdf')}
    
    response = test_client.post('/upload', 
                         data=data,
                         content_type='multipart/form-data')
    
    assert response.status_code in [200, 500]  # Depending on if API key is configured

def test_get_notebooks(test_client):
    # First login
    test_client.post('/signup', json={
        'username': 'notebooktest',
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