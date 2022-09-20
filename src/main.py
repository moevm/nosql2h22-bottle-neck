from flask import Flask, session
app = Flask(__name__)

app.config.update(SECRET_KEY="sdasda")

@app.route('/')
def server():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    return "Hellow world {}".format(session.get('visits'))

if __name__ == "__main__":
    app.run('0.0.0.0')