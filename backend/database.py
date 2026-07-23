from pymongo import MongoClient
from config import MONGODB_URI

client = MongoClient(MONGODB_URI)

try:
    client.admin.command("ping")
    print(" MongoDB Connected Successfully")
except Exception as e:
    print("MongoDB Connection Failed:", e)

db = client["interviewiq"]
interviews_collection = db["interviews"]

