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
BEARER_API_TOKEN = {"Authorization": "Bearer " + os.getenv("API_TOKEN")}


def get_request(url_part: str) -> requests.Response:
    return requests.get(API_URL + url_part, headers=BEARER_API_TOKEN)


def post_request(url_part: str, data: dict) -> requests.Response:
    return requests.post(API_URL + url_part, headers=BEARER_API_TOKEN, json=data)


def delete_request(url_part: str) -> requests.Response:
    return requests.delete(API_URL + url_part, headers=BEARER_API_TOKEN)


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
        data = resp.json()
        if resp.status_code == 200 and data["su"] != {}:
            flask.session["data"] = resp.json()
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
        return flask.render_template("students.html.j2", students=users.json())
    elif flask.request.method == "POST":
        if "delete" in flask.request.form:
            ret = get_request("/users")
            for user in ret.json():
                if user["id"] == flask.request.form["id"]:
                    ret = delete_request(f"/users/{user['username']}/student")
                    print(ret.status_code)
                    users = get_request("/students").json()
                    return flask.render_template("students.html.j2", students=users)
        if "modify" in flask.request.form:
            ret = get_request("/users")
            for user in ret.json():
                if user["id"] == flask.request.form["id"]:
                    return app.redirect(flask.url_for("modify_student", user_name=user["username"]))
            return "There has been an error."
        if "new" in flask.request.form:
            return app.redirect(flask.url_for("new_student"))


@app.route("/students/modify/<user_name>", methods=["GET", "POST"])
def modify_student(user_name: str):
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        student_data = get_request(f"/users/{user_name}/student")
        if student_data.status_code != 200:
            return "There has been an error."
        return flask.render_template("modify_student.html.j2", user_data=student_data.json())


@app.route("/teachers", methods=["GET", "POST"])
def teachers():
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        users = get_request("/teachers")
        return flask.render_template("teachers.html.j2", users=users.json())
    elif flask.request.method == "POST":
        pass


@app.route("/classes", methods=["GET", "POST"])
def classes():
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        classes = get_request("/classes")
        return flask.render_template("classes.html.j2", classes=classes.json())
    elif flask.request.method == "POST":
        pass


@app.route("/students/new", methods=["GET", "POST"])
def new_student():
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("Login"), code=401)
    if flask.request.method == "GET":
        return flask.render_template("new_student.html.j2")


if __name__ == "__main__":
    app.run(debug=True)
