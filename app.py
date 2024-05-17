import json

import flask
import dotenv
import os
import requests
import pathlib


dotenv.load_dotenv()
app = flask.Flask(__name__, static_url_path="/static", static_folder=pathlib.Path(__file__).parent / "static")
app.secret_key = os.getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"


API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")


def get_request(url_part: str) -> requests.Response:
    return requests.get(API_URL + url_part, headers={"Authorization": "Bearer " + API_TOKEN})


def post_request(url_part: str, data: dict) -> requests.Response:
    return requests.post(API_URL + url_part, headers={"Authorization": "Bearer " + API_TOKEN}, json=data)


@app.route("/")
@app.route("/home")
def home():
    if "data" in flask.session:
        return flask.render_template("home.html.j2")
    return flask.redirect(flask.url_for("login"), code=401)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "data" in flask.session:
        return flask.redirect(flask.url_for("home"))
    if flask.request.method == "GET":
        return flask.render_template("login.html.j2")
    elif flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        resp = post_request("/login", {"username": username, "password": password})
        flask.session["data"] = resp.json()
        if resp.status_code == 200:
            return flask.redirect(flask.url_for("home"))
        else:
            return flask.render_template("login.html.j2", data_incorrect=True)


@app.route("/logout")
def logout():
    flask.session.pop("data")
    return flask.render_template("logout.html.j2")


@app.route("/students", methods=["GET", "POST"])
def students():
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        users = get_request("/students")
        return flask.render_template("students.html.j2", users=users.json())
    elif flask.request.method == "POST":
        if "delete" in flask.request.form:
            # TODO: Delete User Data
            users = get_request("/students")
            return flask.render_template("students.html.j2", users=users.json())
        if "modify" in flask.request.form:
            ret = get_request(f"/students/{flask.request.form['id']}")
            return app.redirect(flask.url_for("modify_student", student_id=ret.json()["id"]))
        if "new" in flask.request.form:
            return app.redirect(flask.url_for("new_student"))


@app.route("/students/modify/<student_id>")
def modify_student(student_id: str):
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        student_data = get_request(f"/users/{student_id}/student")
        print(student_data.text)
        if student_data.status_code != 200:
            return "There has been an error."
        return flask.render_template("modify.html.j2", user_data=student_data.json())


@app.route("/students/new", methods=["GET", "POST"])
def new_student():
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("Login"), code=401)
    if flask.request.method == "GET":
        return "new"


if __name__ == "__main__":
    app.run(debug=True)
