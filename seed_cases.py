
"""
seed_cases.py
@ken.chen
"""
import os
import json
from pymongo import MongoClient, ReplaceOne

def load_cases(json_path="cases.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def seed_cases(db, json_path="cases.json"):
    cases = load_cases(json_path)
    ops = [ReplaceOne({"_id": c["_id"]}, c, upsert=True) for c in cases]
    if ops:
        result = db.cases.bulk_write(ops)
        return result.upserted_count + result.modified_count
    return 0

if __name__ == "__main__":
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/training"))
    db = client.get_database()
    count = seed_cases(db)
    print("Seeded", count, "cases")
    client.close()
