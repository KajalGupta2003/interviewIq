from pymongo import MongoClient
from config import MONGODB_URI

client = MongoClient(MONGODB_URI)

db = client["interviewiq"]
interviews_collection = db["interviews"]

print(" MongoDB Connected Successfully")