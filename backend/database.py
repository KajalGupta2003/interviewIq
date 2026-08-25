from pymongo import MongoClient
from config import MONGODB_URI

client = MongoClient(MONGODB_URI)

try:
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)

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


# Create indexes once at startup
create_indexes()