#Importing MongoDB and bcrypt modules
from pymongo import MongoClient
from bcrypt import *
import html
#Initialization function for both collections within the DB
def db_init():
    #Creating variables to reference different layers of MongoDB
    # mongo_client = MongoClient("localhost")
    mongo_client = MongoClient("mongo")
    db = mongo_client["CSE312-Project"]
    #Creating collection to reference the chat history
    chat_collection = db["chat"]
    #Creating collection to reference usernames and passwords
    creds_collection = db["credentials"]
    #Creating collection to account for unique IDs
    counter_collection = db["counter"]
    #Checking if the counter collection is initialized already
    if counter_collection.count_documents({}) == 0:
        #If not, initializing it to 0
        counter_collection.insert_one({'count': 0})  
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
    counter_collection = db["counter"]
    #Calling the update_one function to increment the current ID value
    counter_collection.update_one({}, {"$set": {"count": counter_collection.find_one({},{}).get("count") + 1}})

#Function to insert a message into DB
def insert_message(db, message, username):
    #Re-establishing collections to account for chat history and unique IDs
    chat_collection = db["chat"]
    counter_collection = db["counter"]
    #Calling the insert_one function to insert the message into the DB
    chat_collection.insert_one({"username": username, "message": html.escape(message), "id": int(counter_collection.find_one({},{}).get("count"))})

#Function to store new credentials from a registration request in the DB
def store_creds(db, creds):
    #Re-establishing the collection to reference the credentials
    creds_collection = db["credentials"]
    #Creating the salted and hashed password and storing it back in credentials array
    salt = gensalt()
    creds[1] = hashpw(creds[1].encode(), salt)
    #Calling the insert_one function to insert creds into the DB
    creds_collection.insert_one({"username": creds[0], "password": creds[1], "auth_token": b"", "salt": salt})

def check_creds(db, creds):
    creds_collection = db["credentials"]
    #Read the username and plain password sent by the user
    username = creds[0]
    plaintext_password = creds[1]
    #Obtain the database entry with that username in it. If none is found, returns None
    usrnm_check = creds_collection.find_one({"username":username})
    if(usrnm_check is not None):
        #Obtain salt and salted encrypted password
        stored_salt = usrnm_check["salt"]
        stored_password =usrnm_check["password"]
        #Hash and salt the user's attempted passwpord to check if they match
        encrypt_given_password = hashpw(plaintext_password.encode(),stored_salt)
        if(encrypt_given_password == stored_password):
            return usrnm_check
        else:
            return False
    else:
        return False
    
def add_auth(db,creds, auth_token_encrypted):
    creds_collection = db["credentials"]
    # add an auth token every time the user logs in. Change the pre existing (or empty) token to the new one.
    to_add = creds_collection.find_one_and_update(creds,{"$set":{"auth_token":auth_token_encrypted}})

def get_auth_tokens(db,auth_token_from_browser):
    creds_collection = db["credentials"]
    #Check whether the browser's auth token matches that of the user. There can only be one auth token at a time
    auth_token_check = creds_collection.find_one({"auth_token":auth_token_from_browser})
    return auth_token_check


    # creds_collection


