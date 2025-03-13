from flask_pymongo import PyMongo
from flask import Flask

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://carens:9GSwmL3RTPekTJQR@adoptme.vngse.mongodb.net/"
mongo = PyMongo(app)