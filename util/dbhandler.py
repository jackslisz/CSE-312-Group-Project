#Importing MongoDB
from pymongo import MongoClient

#Initialization function for both collections within the DB
def db_init():
    #Creating variables to reference different layers of MongoDB
    mongo_client = MongoClient("mongo")
    db = mongo_client["CSE312-Project"]
    #Creating collection to reference the chat history
    chat_collection = db["chat"]
    #Creating collection to reference usernames and passwords
    creds_collection = db["credentials"]
    #Creating collection to account for unique IDs
    counter = db["counter"]
    #Checking if the counter collection is initialized already
    if counter.count_documents({}) == 0:
        #If not, initializing it to 0
        counter.insert_one({'count': 0})  
    #Returning the entire DB to access both collections
    return db

#Function to return all of the chat's history
def get_chat_history(db):
    #Re-establishing the collection to reference the chat history
    chat_collection = db["chat"]
    #Returning all of the chat's history
    return chat_collection.find({}, {"_id": 0})

#Function to increment the unique ID value in the counter collection
def update_id(db):
    #Re-establishing the collection to account for unique IDs
    counter = db["counter"]
    #Calling the update_one function to increment the current ID value
    counter.update_one({}, {"$set": {"count": counter.find_one({},{}).get("count") + 1}})

#Function to insert a message into DB
def insert_message(db, message):
    #Re-establishing collections to account for chat history and unique IDs
    chat_collection = db["chat"]
    counter = db["counter"]
    #Calling the insert_one function to insert the message into the DB
    chat_collection.insert_one({"username": "Guest", "message": message, "id": int(counter.find_one({},{}).get("count"))})