from random import randbytes, randint
from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from flask import request
import db_requests
import config


def generate_session(mongo: MongoClient) -> Database:
    users = mongo.get_database(config.CURRENT_USERS_DB_NAME).get_collection(config.CURRENT_USERS_COLLECTION_NAME)
    while True:
        session_id = randbytes(randint(16, 31)).hex()
        if users.count_documents({"_id": session_id}) == 0:
            users.insert_one({"_id": session_id, "last_time": datetime.now()})
            break
    user_db = mongo.get_database(session_id)
    db_requests.create_user_db(mongo, user_db)
    return user_db


def clear_user_data(mongo: MongoClient, session_id: str):
    mongo.drop_database(session_id)
    users_collection = mongo.get_database(config.CURRENT_USERS_DB_NAME).get_collection(config.CURRENT_USERS_COLLECTION_NAME)
    users_collection.delete_one({"_id": session_id})


def check_session_time(mongo: MongoClient) -> Database:
    session_id = request.cookies.get("session_id")
    users_collection = mongo.get_database(config.CURRENT_USERS_DB_NAME).get_collection(config.CURRENT_USERS_COLLECTION_NAME)
    last_time = users_collection.find_one({"_id": session_id})
    if session_id is None or last_time is None:
        user_db = generate_session(mongo)
        session_id = user_db.name
    elif datetime.now() - last_time["last_time"] > config.TIMEOUT:
        clear_user_data(mongo, session_id)
        user_db = generate_session(mongo)
        session_id = user_db.name
    else:
        user_db = mongo.get_database(session_id)
    users_collection.update_one({"_id": session_id},
                                {"$set": {"last_time": datetime.now()}},
                                upsert=True)
    return user_db


def user_request(mongo: MongoClient, do_something: callable):
    user_db = check_session_time(mongo)
    resp = do_something(user_db)
    resp.set_cookie("session_id", user_db.name, config.TIMEOUT)
    return resp


def check_and_clear_user_data(mongo: MongoClient):
    now = datetime.now()
    delete_users = []
    users = mongo.get_database(config.CURRENT_USERS_DB_NAME).get_collection(config.CURRENT_USERS_COLLECTION_NAME)
    for user in users.find({}):
        if now - user["last_time"] > config.TIMEOUT:
            delete_users.append(user["_id"])
    for user_id in delete_users:
        clear_user_data(mongo, user_id)
