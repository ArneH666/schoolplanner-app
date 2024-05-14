import flask
import dotenv
import os
import requests


dotenv.load_dotenv()
app = flask.Flask(__name__, static_url_path="/static")


API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")


def get_request(url_part: str) -> requests.Response:
    return requests.get(API_URL + url_part, headers={"Authorization": "Bearer " + API_TOKEN})


def post_request(url_part: str, data: {}) -> requests.Response:
    return requests.post(API_URL + url_part, headers={"Authorization": "Bearer " + API_TOKEN})


@app.route("/")
def index():
    return flask.redirect(flask.url_for("home"))


@app.route("/home")
def home():
    return flask.render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")
    elif flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        resp = post_request("/login", {"username": username, "password": password})
        print(resp.status_code)
        if resp.status_code == 200:
            return flask.redirect(flask.url_for("home"))
        else:
            return flask.render_template("login.html", data_incorrect=True)


@app.route("/students", methods=["GET", "POST"])
def students():
    if flask.request.method == "GET":
        return flask.render_template("students.html")
    elif flask.request.method == "POST":
        if "delete" in flask.request.form:
            # TODO: Delete User Data
            return flask.render_template("students.html")
        if "change" in flask.request.form:
            return app.redirect(flask.url_for("modify_student", student_id=flask.request.form["id"]))
        if "new" in flask.request.form:
            return app.redirect(flask.url_for("new_student"))


@app.route("/students/modify/<student_id>")
def modify_student(student_id: str):
    if flask.request.method == "GET":
        return flask.render_template("modify.html")


@app.route("/students/new", methods=["GET", "POST"])
def new_student():
    if flask.request.method == "GET":
        return "new"


if __name__ == "__main__":
    app.run(debug=True)
