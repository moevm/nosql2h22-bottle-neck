import overpy
from pymongo import MongoClient
from config import AREA_POLYGON, TYPE_CAPACITY, ORIGIN_DB_NAME


def load_data(database):
    """
    Load OSM data to given mongo database
    :param database: Mongo database
    :return:
    """

    def add_ways(road):
        # Add ways to given road
        neighbours = roads_collection.find({"start": road['end']})
        ways = [neighbour["_id"] for neighbour in neighbours]
        roads_collection.update_one({"_id": road["_id"]}, {"$set": {"ways": ways}})

    api = overpy.Overpass()
    roads_collection = database.roads

    # Fetch all roads and nodes in area
    result = api.query(f"""
        way (poly:"{AREA_POLYGON}")
          ["highway"~"^(motorway|trunk|primary|secondary|residential|tertiary|secondary_link)$"]; 
        (._;>;);
        out;
        """)

    for way in result.ways:
        node_list = way.nodes
        for i in range(1, len(node_list)):
            roads_collection.insert_one(
                {"start": [float(node_list[i - 1].lon), float(node_list[i - 1].lat)],
                 "end": [float(node_list[i].lon), float(node_list[i].lat)],
                 "capacity": TYPE_CAPACITY[way.tags["highway"]],
                 "car_count": 0, "workload": 0,
                 "address": way.tags.get("name", 'n/a')}
            )

            # Reverse direction if present
            if way.tags.get("oneway", "no") == "no":
                roads_collection.insert_one(
                    {"end": [float(node_list[i - 1].lon), float(node_list[i - 1].lat)],
                     "start": [float(node_list[i].lon), float(node_list[i].lat)],
                     "capacity": TYPE_CAPACITY[way.tags["highway"]],
                     "car_count": 0, "workload": 0,
                     "address": way.tags.get("name", 'n/a')}
                )
    for current_road in roads_collection.find():
        add_ways(current_road)


def load_data_to_origin():
    """
    Load new roads data to origin database
    :return:
    """
    client = MongoClient('mongodb://db', 27017)
    database = client[ORIGIN_DB_NAME]
    # Drop roads if present
    database.roads.drop()
    load_data(database)


if __name__ == '__main__':
    load_data_to_origin()
