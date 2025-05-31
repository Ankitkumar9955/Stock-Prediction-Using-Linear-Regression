import json
import os

AUTH_FILE = "users.json"  # File to store user credentials

def load_users():
    """Load user data from file"""
    if not os.path.exists(AUTH_FILE):
        return {}  # Return empty if file doesn't exist
    with open(AUTH_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """Save user data to file"""
    with open(AUTH_FILE, "w") as f:
        json.dump(users, f, indent=4)

def signup(username, password):
    """Handles user signup"""
    users = load_users()
    
    if username in users:
        return False, "❌ Username already exists!"
    
    users[username] = password  # Store plaintext (⚠️ Use hashing in production)
    save_users(users)
    
    return True, "✅ Signup successful!"

def login(username, password):
    """Handles user login"""
    users = load_users()
    
    if username not in users:
        return False, "❌ User not found!"
    
    if users[username] != password:
        return False, "❌ Incorrect password!"
    
    return True, "✅ Login successful!"
