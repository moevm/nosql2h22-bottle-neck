import overpy


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
    result = api.query("""
        way (poly:"59.980147421963146 30.312250094337468 59.972445424303565 30.2844249624462 59.96622566894886 30.278736936798886 59.96453869723286 30.26332214571193 59.949347482877776 30.284507653922166 59.94587234907377 30.306962011432642 59.946546084908604 30.319483336580884 59.95416225858059 30.34000898935265 59.9610169995363 30.335965638419612 59.97215932606719 30.33173135922497 59.97847216741082 30.322286587299565")
          ["highway"~"^(motorway|trunk|primary|secondary|residential|tertiary|secondary_link)$"]; 
        (._;>;);
        out;
        """)

    for way in result.ways:
        node_list = way.nodes
        for i in range(1, len(node_list)):
            roads_collection.insert_one(
                {"start": [float(node_list[i - 1].lat), float(node_list[i - 1].lon)],
                 "end": [float(node_list[i].lat), float(node_list[i].lon)],
                 "capacity": 0, "car_count": 0, "workload": 0,
                 "address": way.tags.get("name", 'n/a')}
            )

            # Reverse direction if present
            if way.tags.get("oneway", "no") == "no":
                roads_collection.insert_one(
                    {"end": [float(node_list[i - 1].lat), float(node_list[i - 1].lon)],
                     "start": [float(node_list[i].lat), float(node_list[i].lon)],
                     "capacity": 0, "car_count": 0, "workload": 0,
                     "address": way.tags.get("name", 'n/a')}
                )
    for current_road in roads_collection.find():
        add_ways(current_road)
