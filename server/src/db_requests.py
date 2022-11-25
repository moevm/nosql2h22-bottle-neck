from pymongo.database import Database
from pymongo import MongoClient, GEO2D
from utils import transform_roads
import drawing
import config


def create_user_db(mongo: MongoClient, user_db: Database):
    origin_roads = mongo.get_database(config.ORIGIN_DB_NAME).get_collection("roads").find()
    origin_roads, min_x, min_y, x_diff, y_diff = transform_roads(origin_roads)
    user_db.get_collection("data").insert_one({
        "name": "coords",
        "min_x": min_x,
        "min_y": min_y,
        "x_coeff": config.MAP_IMAGE_SIZE[0] / x_diff,
        "y_coeff": config.MAP_IMAGE_SIZE[1] / y_diff
    })
    user_db.get_collection("roads").create_index([("location", GEO2D)], min=-config.MAX_COORDINATE, max=config.MAX_COORDINATE)
    user_db.get_collection("roads").insert_many(origin_roads)
    create_map_image(user_db)


def create_map_image(user_db: Database, with_workload=False):
    roads = user_db.get_collection("roads").find()
    min_x, min_y, x_coeff, y_coeff = get_coordinates(user_db)
    img_bytes = drawing.create_map_image(roads, config.MAP_IMAGE_SIZE, min_x, min_y, x_coeff, y_coeff, with_workload)
    user_db.get_collection("data").update_one(
        {"name": "map_image"},
        {
            "$set": {"name": "map_image", "data": img_bytes}
        },
        upsert=True
    )


def get_coordinates(user_db: Database):
    coords = user_db.get_collection("data").find_one({"name": "coords"})
    return coords["min_x"], coords["min_y"], coords["x_coeff"], coords["y_coeff"]


def get_roads_with_polygon(user_db: Database, polygon: list[tuple[float, float]]):
    return user_db.get_collection("roads").find({
        "location": {
            "$geoWithin": {"$polygon": polygon}
        }
    })


def update_roads(user_db: Database, roads: list[dict]):
    roads_collection = user_db.get_collection("roads")
    for road in roads:
        roads_collection.update_one(
            {
                "_id": road["_id"]
            },
            {
                "$set": {
                    "workload": road["workload"],
                    "car_count": road["car_count"]
                }
            },
            upsert=True
        )


def get_map_image(user_db: Database):
    img = user_db.get_collection("data").find_one({"name": "map_image"})
    return img["data"] if img is not None else bytes("no data", "UTF-8")
