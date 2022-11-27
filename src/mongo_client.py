import pymongo

myclient = pymongo.MongoClient("mongodb://mongodb:27017/")
db = myclient["users"]
users_collection = db["users"]
results_collection = db["results"]