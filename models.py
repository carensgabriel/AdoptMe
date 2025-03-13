from database import mongo
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, password):
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)  # Hash password
    user = {
        "username": username, 
        "password": hashed_password, 
        "role": "user"}  # Simpan hashed password
    mongo.db.users.insert_one(user)

def check_user(username, password):
    user = mongo.db.users.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return True
    return False