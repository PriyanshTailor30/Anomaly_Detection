# models/__init__.py
from flask import Flask

# Initialize Flask app
app = Flask(__name__, template_folder='../templates') 
app._static_folder = '../static'
app.secret_key = "secret key"

# Import routes to register them with the Flask app
from src import routes
from src import dbconfig