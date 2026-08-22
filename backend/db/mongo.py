import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception(" MONGO_URI not found in environment variables")

# Create MongoDB client
client = MongoClient(MONGO_URI)

# Select database
db = client["interview_db"]

# Collections
users_collection = db["users"]
interviews_collection = db["interviews"]



def create_indexes():
    # Unique email for users
    users_collection.create_index("user_email", unique=True)

    # Faster queries for user interviews
    interviews_collection.create_index("email")

    # Sort by latest interviews
    interviews_collection.create_index("created_at")


# Call once at startup
create_indexes()