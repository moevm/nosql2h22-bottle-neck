import json
from flask import Flask, make_response, Response, request, send_file
from pymongo import MongoClient
from io import BytesIO
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
    point1 = utils.convert_image_coordinates_to_real((float(data['point1']['x']), float(data['point1']['y'])),
                                                     min_x, min_y, x_coeff, y_coeff, config.MAP_IMAGE_MARGIN)
    point2 = utils.convert_image_coordinates_to_real((float(data['point2']['x']), float(data['point2']['y'])),
                                                     min_x, min_y, x_coeff, y_coeff, config.MAP_IMAGE_MARGIN)
    radius = utils.convert_radius_scale_to_real(float(data['radius']), x_coeff, y_coeff)
    car_count = int(data['car_count'])
    if car_count <= 0:
        return make_response("Car count must be positive", 400)

    polygon = utils.approximate_ellipse(point1, point2, radius, config.N)
    roads = db_requests.get_roads_with_polygon(users_db, session_id, polygon)
    road_point1 = db_requests.get_closest_road_in_polygon(users_db, session_id, polygon, list(point1))
    road_point2 = db_requests.get_closest_road_in_polygon(users_db, session_id, polygon, list(point2))
    updated_roads, routes = utils.simulate(roads, car_count, road_point1["_id"], road_point2["_id"])
    if len(updated_roads) == 0:
        return make_response("No roads", 400)
    if len(routes) == 0:
        return make_response("No routes", 400)
    db_requests.check_and_clear_prev_simulation(users_db, session_id)
    db_requests.update_roads(users_db, updated_roads)
    db_requests.insert_routes(users_db, session_id, routes)
    db_requests.create_map_image(users_db, session_id, True)
    return make_response()


def clear_data(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    return make_response(db_requests.clear_data(users_db, session_id))


def export_data(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    data = db_requests.export_data(users_db, session_id)
    out_stream = BytesIO()
    out_stream.write(json.dumps(data).encode())
    out_stream.seek(0)
    return send_file(out_stream, mimetype='application/json', as_attachment=True, download_name='export.json')


def import_data(session_id: str) -> Response:
    users_db = client.get_database(config.CURRENT_USERS_DB_NAME)
    import_file = request.files['import']
    data = json.load(import_file.stream)
    if db_requests.import_data(users_db, session_id, data):
        return make_response()
    else:
        return make_response("Bad import file", 400)


@app.route('/')
def server():
    return user_request(client, main_page)


@app.route('/map_image')
def server_image():
    return user_request(client, get_image)


@app.route('/roads', methods=["GET"])
def roads():
    return user_request(client, get_roads)


@app.route('/routes', methods=["GET"])
def ways():
    return user_request(client, get_ways)


@app.route('/simulate', methods=["POST"])
def simulate():
    return user_request(client, update_image)


@app.route('/clear', methods=["DELETE"])
def clear():
    return user_request(client, clear_data)


@app.route('/export', methods=["GET"])
def export_route():
    return user_request(client, export_data)


@app.route('/import', methods=["POST"])
def import_route():
    return user_request(client, import_data)


def on_start():
    db_requests.create_users_db(client)


if __name__ == "__main__":
    on_start()
    app.run('0.0.0.0', config.PORT)
