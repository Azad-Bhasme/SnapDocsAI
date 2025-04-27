# In-memory users store (no database used here)
users_db = {}

def authenticate_user(username, password):
    return users_db.get(username) == password

def register_user(username, password):
    if username in users_db:
        return False
    users_db[username] = password
    return True
