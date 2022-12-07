from random import randbytes
from datetime import datetime
from pymongo import MongoClient
from flask import request
import db_requests
import config


def generate_session(mongo: MongoClient) -> str:
    users_info = mongo.get_database(config.CURRENT_USERS_DB_NAME).users_info
    while True:
        session_id = randbytes(120).hex()
        if users_info.find_one({"_id": session_id}) is None:
            users_info.insert_one({
                "_id": session_id,
                "date": datetime.utcnow()
            })
            break
    db_requests.create_user_data(mongo, session_id)
    return session_id


def check_session_time(mongo: MongoClient) -> str:
    session_id = request.cookies.get("bottle_neck_session_id")
    users_collection = mongo.get_database(config.CURRENT_USERS_DB_NAME).users_info
    if session_id is None or users_collection.find_one({"_id": session_id}) is None:
        session_id = generate_session(mongo)
    timeout_update = config.TIMEOUT.total_seconds() * config.TIMEOUT_UPDATE
    if (datetime.utcnow() - users_collection.find_one({"_id": session_id})["date"]).total_seconds() > timeout_update:
        db_requests.update_dates(mongo.get_database(config.CURRENT_USERS_DB_NAME), session_id)
    return session_id


def user_request(mongo: MongoClient, do_something: callable):
    session_id = check_session_time(mongo)
    resp = do_something(session_id)
    resp.set_cookie("bottle_neck_session_id", session_id, config.TIMEOUT, samesite="Strict")
    return resp
