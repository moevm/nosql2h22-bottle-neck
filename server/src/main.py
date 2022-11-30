from flask import Flask, make_response, Response, request
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


def get_roads(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    return make_response(db_requests.filter_roads(users_db, session_id, request.args))


def get_ways(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    return make_response(db_requests.filter_ways(users_db, session_id, request.args))


def update_image(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    min_x, min_y, x_coeff, y_coeff = db_requests.get_scale_parameters(users_db, session_id)

    data = request.get_json()
    point1 = (data['point1']['x'] / x_coeff + min_x, data['point1']['y'] / y_coeff + min_y)
    point2 = (data['point2']['x'] / x_coeff + min_x, data['point2']['y'] / y_coeff + min_y)
    radius = data['radius']
    radius = utils.convert_radius_scale_to_real(radius, x_coeff, y_coeff)
    car_count = data['car_count']

    polygon = utils.approximate_ellipse(point1, point2, radius, config.N)
    roads = db_requests.get_roads_with_polygon(users_db, session_id, polygon)
    updated_roads, routes = utils.simulate(roads, car_count)
    db_requests.update_roads(users_db, updated_roads)
    db_requests.insert_routes(users_db, session_id, routes)
    db_requests.create_map_image(users_db, session_id, True)
    resp = make_response(";".join([f"({p[0]}, {p[1]})" for p in polygon]))
    return resp


def clear_data(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    return make_response(db_requests.clear_data(users_db, session_id))


@app.route('/')
def server():
    return user_request(client, main_page)


@app.route('/map_image')
def server_image():
    return user_request(client, get_image)


@app.route('/roads', methods=["GET"])
def roads():
    return user_request(client, get_roads)


@app.route('/ways', methods=["GET"])
def ways():
    return user_request(client, get_ways)


@app.route('/simulate', methods=["POST"])
def simulate():
    return user_request(client, update_image)


@app.route('/clear', methods=["GET"])
def clear():
    return user_request(client, clear_data)


def on_start():
    db_requests.create_users_db(client)


if __name__ == "__main__":
    on_start()
    app.run('0.0.0.0', config.PORT)
