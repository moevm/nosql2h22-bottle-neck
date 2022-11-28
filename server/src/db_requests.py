from datetime import datetime
from pymongo.database import Database
from pymongo import MongoClient, GEO2D
from bson.json_util import dumps
from utils import transform_roads
import drawing
import config


def create_users_db(mongo: MongoClient):
    db = mongo.get_database(config.CURRENT_USERS_DB_NAME)
    roads = db.get_collection("roads")
    roads_indexes = roads.index_information()
    if roads_indexes.get(config.TTL_INDEX_NAME) is None:
        roads.create_index("date", expireAfterSeconds=int(config.TIMEOUT.total_seconds()), name=config.TTL_INDEX_NAME)
    if roads_indexes.get(config.GEOINDEX_INDEX_NAME) is None:
        roads.create_index(
            [("location", GEO2D)],
            min=-config.MAX_COORDINATE,
            max=config.MAX_COORDINATE,
            name=config.GEOINDEX_INDEX_NAME
        )
    routes = db.get_collection("routes")
    routes_indexes = routes.index_information()
    if routes_indexes.get(config.TTL_INDEX_NAME) is None:
        routes.create_index("date", expireAfterSeconds=int(config.TIMEOUT.total_seconds()), name=config.TTL_INDEX_NAME)
    users_info = db.get_collection("users_info")
    users_info_indexes = users_info.index_information()
    if users_info_indexes.get(config.TTL_INDEX_NAME) is None:
        users_info.create_index("date", expireAfterSeconds=int(config.TIMEOUT.total_seconds()),
                                name=config.TTL_INDEX_NAME)


def create_user_data(mongo: MongoClient, session_id: str):
    origin_roads = mongo.get_database(config.ORIGIN_DB_NAME).get_collection("roads").find()
    origin_roads, min_x, min_y, x_diff, y_diff = transform_roads(origin_roads)
    mongo.get_database(config.CURRENT_USERS_DB_NAME).users_info.update_one(
        {
            "_id": session_id
        },
        {
            "$set": {
                "scale": {
                    "min_x": min_x,
                    "min_y": min_y,
                    "x_coeff": config.MAP_IMAGE_SIZE[0] / x_diff,
                    "y_coeff": config.MAP_IMAGE_SIZE[1] / y_diff
                }
            }
        }
    )
    roads_new_ids = {}
    roads_collection = mongo.get_database(config.CURRENT_USERS_DB_NAME).roads
    for road in origin_roads:
        prev_id = road["_id"]
        temp_road = road.copy()
        del temp_road["_id"]
        temp_road["user"] = session_id
        new_road_id = roads_collection.insert_one(temp_road).inserted_id
        roads_new_ids[prev_id] = new_road_id
    for road in origin_roads:
        new_road_id = roads_new_ids[road["_id"]]
        roads_collection.update_one(
            {"_id": new_road_id},
            {
                "$set": {
                    "ways": [roads_new_ids[next_id] for next_id in road["ways"]],
                    "date": datetime.utcnow()
                }
            }
        )
    create_map_image(mongo.get_database(config.CURRENT_USERS_DB_NAME), session_id)


def create_map_image(users_db: Database, session_id: str, with_workload=False):
    roads = users_db.roads.find({"user": session_id})
    min_x, min_y, x_coeff, y_coeff = get_scale_parameters(users_db, session_id)
    img_bytes = drawing.create_map_image(roads, config.MAP_IMAGE_SIZE, min_x, min_y, x_coeff, y_coeff, with_workload)
    users_db.users_info.update_one(
        {"_id": session_id},
        {
            "$set": {
                "map_image": img_bytes,
                "date": datetime.utcnow()
            }
        },
        upsert=True
    )


def get_scale_parameters(users_db: Database, session_id: str):
    coords = users_db.users_info.find_one({"_id": session_id})["scale"]
    return coords["min_x"], coords["min_y"], coords["x_coeff"], coords["y_coeff"]


def get_roads_with_polygon(users_db: Database, session_id: str, polygon: list[tuple[float, float]]):
    return users_db.roads.find({
        "user": session_id,
        "location": {
            "$geoWithin": {"$polygon": polygon}
        }
    })


def filter_roads(users_db: Database, session_id: str,
                 min_workload: float, max_workload: float,
                 address_part: str, road_type: str):
    return dumps(list(users_db.roads.find({
        "user": session_id,
        "workload": {
            "$gte": min_workload,
            "$lte": max_workload
        },
        "address": {
            "$regex": address_part
        },
        "type": road_type
    })))


def filter_ways(users_db: Database, session_id: str,
                min_length: float, max_length: float,
                min_time: float, max_time: float):
    return dumps(list(users_db.routes.find({
        "user": session_id,
        "length": {
            "$gte": min_length,
            "$lte": max_length
        },
        "time": {
            "$gte": min_time,
            "$lte": max_time,
        }
    })))


def update_roads(users_db: Database, roads: list[dict]):
    roads_collection = users_db.roads
    for road in roads:
        roads_collection.update_one(
            {
                "_id": road["_id"]
            },
            {
                "$set": {
                    "workload": road["workload"],
                    "car_count": road["car_count"],
                    "date": datetime.utcnow()
                }
            },
            upsert=True
        )


def clear_roads(users_db: Database, session_id: str):
    clear_request = users_db.roads.update_many({"user": session_id, "workload": {"$exists": True}},
                                               {"$unset": {"workload": ""}})
    return dumps({"modified_count": clear_request.modified_count})


def get_map_image(users_db: Database, session_id: str):
    user_info = users_db.users_info.find_one({"_id": session_id})
    if user_info is None:
        user_info = {}
    return user_info.get("map_image", bytes("no data", "UTF-8"))
