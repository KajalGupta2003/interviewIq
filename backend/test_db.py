from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URI")

try:
    client = MongoClient(uri)
    
    # Try to access DB
    db = client["ai_interview"]
    
    # Force connection check
    client.admin.command('ping')

    print("✅ Connected to MongoDB successfully!")
    
    print("📂 Collections:", db.list_collection_names())

except Exception as e:
    print("❌ Connection failed:", e)