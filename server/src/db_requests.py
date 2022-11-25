from pymongo.database import Database
from pymongo import MongoClient
from utils import transform_roads
import drawing
import config


def create_user_db(mongo: MongoClient, user_db: Database):
    origin_roads = mongo.get_database(config.ORIGIN_DB_NAME).get_collection("roads").find()
    origin_roads = transform_roads(origin_roads)
    user_db.get_collection("roads").insert_many(origin_roads)
    create_map_image(user_db)


def create_map_image(user_db: Database, with_workload=False):
    roads = user_db.get_collection("roads").find()
    img_bytes = drawing.create_map_image(roads, config.MAP_IMAGE_SIZE, with_workload)
    user_db.get_collection("data").update_one(
        {"name": "map_image"},
        {
            "$set": {"name": "map_image", "data": img_bytes}
        },
        upsert=True
    )


def get_map_image(user_db: Database):
    img = user_db.get_collection("data").find_one({"name": "map_image"})
    return img["data"] if img is not None else bytes("no data", "UTF-8")
