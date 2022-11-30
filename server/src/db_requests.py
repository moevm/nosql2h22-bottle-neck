from datetime import datetime
from pymongo.database import Database
from pymongo import MongoClient, GEO2D
from bson.json_util import dumps
from utils import transform_roads, scale_roads, scale_routes
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


def filter_roads(users_db: Database, session_id: str, request_args: dict):
    # Transform get request args to mongo query
    filter_request = {"user": session_id}

    min_workload = request_args.get("min")
    max_workload = request_args.get("max")
    if min_workload is not None or max_workload is not None:
        filter_request["workload"] = {}
    else:
        filter_request["workload"] = {"$exists": True}
    if min_workload is not None:
        filter_request["workload"]["$gte"] = float(min_workload)
    if max_workload is not None:
        filter_request["workload"]["$lte"] = float(max_workload)

    address = request_args.get("address")
    if address is not None:
        filter_request["address"] = {"$regex": address}

    road_type = request_args.get("type")
    if road_type is not None:
        filter_request["type"] = road_type

    filtered_roads = users_db.roads.find(filter_request)

    # Scale roads coordinates to map image
    min_x, min_y, x_coeff, y_coeff = get_scale_parameters(users_db, session_id)
    filtered_roads = list(filtered_roads)
    scale_roads(list(filtered_roads), min_x, min_y, x_coeff, y_coeff)
    return dumps(filtered_roads)


def filter_ways(users_db: Database, session_id: str, request_args: dict):
    # Transform get request args to mongo query
    filter_request = {"user": session_id}
    min_length = request_args.get("minLength")
    max_length = request_args.get("maxLength")
    if min_length is not None or max_length is not None:
        filter_request["length"] = {}
    if min_length is not None:
        filter_request["length"]["$gte"] = float(min_length)
    if max_length is not None:
        filter_request["length"]["$lte"] = float(max_length)

    min_time = request_args.get("minTime")
    max_time = request_args.get("maxTime")
    if min_time is not None or max_time is not None:
        filter_request["time"] = {}
    if min_time is not None:
        filter_request["time"]["$gte"] = float(min_time)
    if max_time is not None:
        filter_request["time"]["$lte"] = float(max_time)

    filtered_routes = users_db.routes.find(filter_request)
    # Scale routes coordinates to map image
    min_x, min_y, x_coeff, y_coeff = get_scale_parameters(users_db, session_id)
    filtered_routes = list(filtered_routes)
    scale_routes(filtered_routes, min_x, min_y, x_coeff, y_coeff)
    return dumps(filtered_routes)


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


def insert_routes(users_db: Database, session_id: str, routes: list[dict]):
    for route in routes:
        route["user"] = session_id
    return dumps({"acknowledged": users_db.routes.insert_many(routes).acknowledged})


def clear_data(users_db: Database, session_id: str):
    clear_roads_request = users_db.roads.update_many({"user": session_id, "workload": {"$exists": True}},
                                                     {"$unset": {"workload": ""}})
    users_db.routes.drop()
    return dumps({"modified_roads_count": clear_roads_request.modified_count,
                  "routes_dropped": True})


def get_map_image(users_db: Database, session_id: str):
    user_info = users_db.users_info.find_one({"_id": session_id})
    if user_info is None:
        user_info = {}
    return user_info.get("map_image", bytes("no data", "UTF-8"))
