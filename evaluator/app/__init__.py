from flask import Flask
import socket
import app.Node as Node

# Initialize the app
app = Flask(__name__, instance_relative_config=True)

# Load the config file
app.config.from_object('config')

host = socket.gethostbyname(socket.gethostname())
node = Node.Node(host)

# Load the controller
from app import controller