from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
app.config.update(SECRET_KEY="sdasda")

client = MongoClient('mongodb://db', 27017)
database = client.flask_db
collection = database.collection


def inc_and_get_value():
    counter_document = collection.find_one({"counter": {"$exists": True}})
    if counter_document is None:
        counter_document = {"counter": 1}
    else:
        counter_document["counter"] += 1
    collection.update_one({"counter": {"$exists": True}},
                          {"$set": counter_document},
                          upsert=True)
    return counter_document["counter"]


@app.route('/')
def server():
    return f"Hello world {inc_and_get_value()}"


if __name__ == "__main__":
    app.run('0.0.0.0')
