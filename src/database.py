
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client.jarvis # Use a database named 'jarvis'
users_collection = db.users # Use a collection named 'users'

def save_credentials(user_id: str, creds_json: str):
    """Save or update user credentials in the database."""
    users_collection.update_one(
        {'user_id': user_id},
        {'$set': {'google_creds_json': creds_json}},
        upsert=True # Create the document if it doesn't exist
    )

def get_credentials(user_id: str) -> str | None:
    """Retrieve user credentials from the database."""
    user_data = users_collection.find_one({'user_id': user_id})
    if user_data:
        return user_data.get('google_creds_json')
    return None
