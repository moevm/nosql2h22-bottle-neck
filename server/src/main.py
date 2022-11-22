import time
import threading
from flask import Flask, make_response, Response
from pymongo import MongoClient
from pymongo.database import Database
from sessions_management import user_request, check_and_clear_user_data
import db_requests
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


@app.route('/')
def server():
    return user_request(client, main_page)


@app.route('/map_image')
def server_image():
    return user_request(client, get_image)  


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
