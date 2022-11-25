import datetime

# Server settings
TIMEOUT = datetime.timedelta(days=1)
PORT = 5000
MONGO_PORT = 27017

# Database names
CURRENT_USERS_DB_NAME = "current_users"
CURRENT_USERS_COLLECTION_NAME = "current_users"
ORIGIN_DB_NAME = "origin_data"  # Origin database name
MAP_IMAGE_SIZE = (800, 800)  # in pixels

# GeoCoordinates
FROM_EPSG = "EPSG:4326"
TO_EPSG = "EPSG:3857"
# TO_EPSG = "EPSG:32636"  # Saint Petersburg region
N = 64
MAX_COORDINATE = 10 ** 9

# Data loading config
# Area for loading
AREA_POLYGON = \
    "59.980147421963146 30.312250094337468 " \
    "59.972445424303565 30.2844249624462 " \
    "59.96622566894886 30.278736936798886 " \
    "59.96453869723286 30.26332214571193 " \
    "59.949347482877776 30.284507653922166 " \
    "59.94587234907377 30.306962011432642  " \
    "59.946546084908604 30.319483336580884 " \
    "59.95416225858059 30.34000898935265 " \
    "59.9610169995363 30.335965638419612 " \
    "59.97215932606719 30.33173135922497 " \
    "59.97847216741082 30.322286587299565"

# Type - capacity correspondence
TYPE_CAPACITY = {
    'motorway': 20,
    'trunk': 15,
    'primary': 10,
    'secondary': 5,
    'residential': 3,
    'tertiary': 3,
    'secondary_link': 5
}
