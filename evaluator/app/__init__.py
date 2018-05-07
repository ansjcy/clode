from flask import Flask
import app.Node as Node
import socket

# Initialize the app
app = Flask(__name__, instance_relative_config=True)

# Load the config file
app.config.from_object('config')

hostname = socket.gethostname()
node = Node.Node(hostname)
node.config()

# Load the controller
from app import controller