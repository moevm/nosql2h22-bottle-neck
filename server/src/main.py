from asyncio import create_subprocess_exec
import time
import threading
from flask import Flask, make_response, Response
from pymongo import MongoClient
from pymongo.database import Database
from sessions_management import user_request, check_and_clear_user_data
import db_requests
import utils
import config


app = Flask(__name__)
app.config.update(SECRET_KEY="sdasda")

client = MongoClient('mongodb://db', config.MONGO_PORT)


def main_page(user_db: Database) -> Response:
    return make_response(f'Map image:<br><img src="/map_image" alt="alternatetext">')


def get_image(user_db: Database) -> Response:
    resp = make_response(db_requests.get_map_image(user_db))
    resp.headers.set("Content-Type", "image/png")
    return resp


def update_image(user_db: Database) -> Response:
    min_x, min_y, x_coeff, y_coeff = db_requests.get_coordinates(user_db)
    p1 = (300 / x_coeff + min_x, 300 / y_coeff + min_y)
    p2 = (500 / x_coeff + min_x, 500 / y_coeff + min_y)
    r = (100 / x_coeff, 100 / y_coeff)
    c = 100
    polygon = utils.approximate_ellipse(p1, p2, r, config.N)
    roads = db_requests.get_roads_with_polygon(user_db, polygon)
    updated_roads, ways = utils.simulate(roads, c)
    db_requests.update_roads(user_db, updated_roads)
    db_requests.create_map_image(user_db, True)
    resp = make_response(";".join([f"({p[0]}, {p[1]})" for p in polygon]))
    return resp


@app.route('/')
def server():
    return user_request(client, main_page)


@app.route('/map_image')
def server_image():
    return user_request(client, get_image)  


@app.route('/simulate', methods=["POST"])
def simulate():
    return user_request(client, update_image)


def periodic_task():
    while True:
        check_and_clear_user_data(client)
        time.sleep(config.TIMEOUT.total_seconds())


def on_start():
    check_and_clear_user_data(client)


if __name__ == "__main__":
    on_start()
    threading.Thread(target=periodic_task).start()
    app.run('0.0.0.0', config.PORT)
