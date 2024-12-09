JuPDFter
Description:
This Project creates a Jupyter notebook upon a given command given through text , pdf , or docx. 
The project allows to create coherent and error free notebooks that will allow users to better understand the topic at hand.
The books that are created by large langauge models like chatgbt , claude and gemini are limited by the token limit for each transaction. Where the code token is more costly in the terms of computation than the normal text token.
JuPDFter solves this by using an extra layer for software engineering that compiles multiple notebooks into a one notebook that helps the user to better understand the specific problem at hand

Capabilitites:
Generate long and detailed notebooks
Generate multiple notebooks from the same prompt, where if instructed JuPDFter will generate books from the basics up to the topic.
Generate books from given pdfs up to 200 pages!
Error handling and correction. 


Prerequisites
Python 3.x
Node.js and npm
Docker

Installation:
  Backend:
    Clone the repository:
    git clone <repository-url>
    Navigate to the backend directory:
    cd backend
    Create and activate a virtual environment:
    store your api key in your .env file
    pip install -r requirements.txt

    Docker:
    install the docker from the official page
    pull the image of postgresSQL

  
  Frontend:
  Navigate to the frontend directory:
  cd frontend
  npm install
  
How to Run:
backend app:
  on a new terminal navigate to the backend folder using cd backend or applicable command on your OS
  start backend app: python app.py
  run the container and connect to it via a connecting string command
frontend:
  on a seperate terminal navigate and open the frontend folder
  start react app : npm start

Note:
both the backend and frontend have sample test such as test_app.py that will help troubleshoot any problem. Happy testing!

