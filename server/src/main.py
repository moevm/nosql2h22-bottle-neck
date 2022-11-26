from flask import Flask, make_response, Response
from pymongo import MongoClient
from sessions_management import user_request
import db_requests
import utils
import config


app = Flask(__name__)
app.config.update(SECRET_KEY="sdasda")

client = MongoClient('mongodb://db', config.MONGO_PORT)


def main_page(session_id: str) -> Response:
    return make_response(f'Map image:<br><img src="/map_image" alt="alternatetext">')


def get_image(session_id: str) -> Response:
    resp = make_response(db_requests.get_map_image(client.get_database(config.CURRENT_USERS_DB_NAME), session_id))
    resp.headers.set("Content-Type", "image/png")
    return resp


def update_image(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    min_x, min_y, x_coeff, y_coeff = db_requests.get_scale_parameters(users_db, session_id)
    p1 = (300 / x_coeff + min_x, 300 / y_coeff + min_y)
    p2 = (500 / x_coeff + min_x, 500 / y_coeff + min_y)
    r = (100 / x_coeff, 100 / y_coeff)
    c = 100
    polygon = utils.approximate_ellipse(p1, p2, r, config.N)
    roads = db_requests.get_roads_with_polygon(users_db, session_id, polygon)
    updated_roads, routes = utils.simulate(roads, c)
    db_requests.update_roads(users_db, updated_roads)
    db_requests.create_map_image(users_db, session_id, True)
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


def on_start():
    db_requests.create_users_db(client)


if __name__ == "__main__":
    on_start()
    app.run('0.0.0.0', config.PORT)
