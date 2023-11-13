#Importing MongoDB, bcrypt, and HTML modules
from pymongo import MongoClient
from bcrypt import *
from html import *

#Initialization function for both collections within the DB
def db_init():
    #Creating variables to reference different layers of MongoDB
    mongo_client = MongoClient("localhost")
    # mongo_client = MongoClient("localhost")
    db = mongo_client["CSE312-Project-One"]
    #Creating collection to reference the chat history
    chat_collection = db["chat"]
    #Creating collection to reference usernames and passwords
    creds_collection = db["credentials"]
    #Creating collection to account for unique IDs of messages and images
    counter_collection = db["counter"]
    image_counter = db["image_counter"]
    #Checking if the counter collection is initialized already
    if counter_collection.count_documents({}) == 0:
        #If not, initializing it to 0
        counter_collection.insert_one({'count': 0})  
    #Checking if the image counter collection is initialized already
    if image_counter.count_documents({}) == 0:
        #If not, initializing it to 0
        image_counter.insert_one({'count': 0})  
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

#Function to insert a message into DB with websocket
def insert_message_websocket(db, body, username):
    #Re-establishing collections to account for chat history and unique IDs
    chat_collection = db["chat"]
    counter_collection = db["counter"]
    #Calling the insert_one function to insert the message into the DB
    # print(body)
    #{"messageType":"chatMessage","title":"fegfeg","description":"e5h5r","choice1":"h5","choice2":"h5rh","choice3":"r5hr","choice4":"jh","correctanswer":"Choice 1"}
    chat_collection.insert_one({"username": username, "image": "static/img/quizicon.ico", "title": body["title"], "description": body["description"], "choice1": body["choice1"], "choice2": body["choice2"], "choice3": body["choice3"], "choice4": body["choice4"], "correctanswer": body["correctanswer"], "id": int(counter_collection.find_one({},{}).get("count"))})

    # print(chat_collection.find_one({"username":username}))

#Function to increment the unique image ID value in the image counter collection
#This function also adds the image name to the user's credentials profile
def insert_image(db):
    #Re-establishing collections to reference credentials and message/image ID collections
    chat_collection = db["chat"]
    counter_collection = db["counter"]
    image_counter = db["image_counter"]
    #Calling the update_one function to increment the current image ID value
    image_counter.update_one({}, {"$set": {"count": image_counter.find_one({},{}).get("count") + 1}})
    #Creating the images name and storing it in a variable
    image_name = "static/img/image" + str(image_counter.find_one({},{}).get("count")) + ".jpg"
    #Calling the update_one function to add the image name to the users profile
    chat_collection.update_one({"id": counter_collection.find_one({},{}).get("count")}, {"$set": {"image": image_name}})
    #Returning the updated image name
    return image_name

#Function to insert a message into DB
def insert_message(db, body, username):
    #Re-establishing collections to account for chat history and unique IDs
    chat_collection = db["chat"]
    counter_collection = db["counter"]
    #Calling the insert_one function to insert the message into the DB
    # print(body)
    chat_collection.insert_one({"username": username, "title": escape(body[0]), "description": escape(body[1]), "choice1": escape(body[2]), "choice2": escape(body[3]), "choice3": escape(body[4]), "choice4": escape(body[5].replace("}", "")), "correctanswer": escape(body[6]), "id": int(counter_collection.find_one({},{}).get("count")),"likes":0, "likers":[]})

#Function to store new credentials from a registration request in the DB
def store_creds(db, creds):
    #Re-establishing the collection to reference the credentials
    creds_collection = db["credentials"]
    #Creating the salted and hashed password and storing it back in credentials array
    salt = gensalt()
    creds[1] = hashpw(creds[1].encode(), salt)
    #Calling the insert_one function to insert creds into the DB
    creds_collection.insert_one({"username": creds[0], "password": creds[1], "auth_token": b"", "salt": salt})

#Function to authenticate a user given their login request
def check_creds(db, creds):
    #Re-establishing the collection to reference the credentials
    creds_collection = db["credentials"]
    #Read the username and plain password sent by the user
    username = creds[0]
    plaintext_password = creds[1]
    #Obtain the database entry with that username in it. If none is found, returns None
    username_check = creds_collection.find_one({"username":username})
    #Checking if user was found within DB
    if(username_check is not None):
        #If so, obtaining salt and salted encrypted password
        stored_salt = username_check["salt"]
        stored_password = username_check["password"]
        #Hash and salt the user's attempted password to check if they match
        encrypt_given_password = hashpw(plaintext_password.encode(),stored_salt)
        #If statement to verify the passwords
        if(encrypt_given_password == stored_password):
            #If verified, returning username_check (true)
            return username_check
        #Otherwise, returning false to signal a failed verification
        else:
            return False
    #Otherwise, returning false to signal a failed verification
    else:
        return False

#Function to store an auth token in the DB
def add_auth(db,creds, auth_token_encrypted):
    #Re-establishing the collection to reference the credentials
    creds_collection = db["credentials"]
    #Adding an auth token every time the user logs in. Change the pre existing (or empty) token to the new one.
    to_add = creds_collection.find_one_and_update(creds,{"$set":{"auth_token":auth_token_encrypted}})

#Function to retrieve the auth token from browser
def get_auth_tokens(db,auth_token_from_browser):
    #Re-establishing the collection to reference the credentials
    creds_collection = db["credentials"]
    #Checking whether the browser's auth token matches that of the user. There can only be one auth token at a time
    return creds_collection.find_one({"auth_token":auth_token_from_browser})

#Function to update the like count on a post
def get_msg_and_like(db, auth_token_from_browser, objectId):
    #Re-establishing collections to reference the chat history and counter variable
    chat_collection = db["chat"]
    counter_collection = db["counter"]
    #Document with data of the message
    likes = chat_collection.find_one({"id":objectId})
    #List of people who have liked the message
    likers = likes["likers"]
    #Auth token information, to get the username
    get_auth_tokens_value = get_auth_tokens(db,auth_token_from_browser)
    #Checking if the user has already liked this specific post
    # print(likers)
    if(get_auth_tokens_value["username"] in likers):
        #If so, creating a new list with the liked person removed
        likers2 = list(likers)
        likers2.remove(get_auth_tokens_value["username"])
        # print("i deleted and got", likers2)
        #Checking if the user was removed successfully
        # print(get_auth_tokens_value["username"], "is un-liking")
        # print(li)
        if(not likers2):
            #Avoid NoneType error
            chat_collection.find_one_and_update(likes,{"$set":{"likes":likes["likes"]-1,"likers":[]}})
            # print("[[]]")
            #Returning the updated like count
            
            # return likes["likes"]-1
        #Otherwise, updating the post information in DB to remove a like
        else:
            #Update the document with one less like and one less liker
            chat_collection.find_one_and_update(likes,{"$set":{"likes":likes["likes"]-1,"likers":likers2}})
            #Returning the updated like count
            # return likes["likes"]-1
            # print(likers2)
    #Otherwise, updating the post information in DB to add a like
    else:
        #Update the document with one more like and one more liker
        # print(get_auth_tokens_value["username"],"is currently LIKE NEW")
        chat_collection.find_one_and_update(likes,{"$set":{"likes":likes["likes"]+1,"likers":likers+[get_auth_tokens_value["username"]]}})
        #Returning the updated like count
        # return likes["likes"]+1
    # print("after everything",likers)