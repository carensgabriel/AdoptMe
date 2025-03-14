from flask_pymongo import PyMongo
from flask import Flask

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://carens:9GSwmL3RTPekTJQR@adoptme.vngse.mongodb.net/AdoptMe"
# app.config["MONGO_URI"] = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database>?retryWrites=true&w=majority"
mongo = PyMongo(app)