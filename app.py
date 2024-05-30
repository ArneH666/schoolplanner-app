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


def put_request(url_part: str, data: dict) -> requests.Response:
    return requests.put(API_URL + url_part, headers=BEARER_API_TOKEN, json=data)


def delete_request(url_part: str) -> requests.Response:
    return requests.delete(API_URL + url_part, headers=BEARER_API_TOKEN)


@app.route("/")
@app.route("/home")
def home() -> str | flask.Response:
    if "data" in flask.session:
        return flask.render_template("home/home.html.j2")
    return flask.redirect(flask.url_for("login"), code=401)


@app.route("/login", methods=["GET", "POST"])
def login() -> str | flask.Response:
    if "data" in flask.session:
        return flask.redirect(flask.url_for("home"))
    if flask.request.method == "GET":
        return flask.render_template("login/login.html.j2")
    elif flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        resp = post_request("/login", {"username": username, "password": password})
        data = resp.json()
        if resp.status_code == 200 and data["su"] != {}:
            flask.session["data"] = resp.json()
            return flask.redirect(flask.url_for("home"))
        else:
            return flask.render_template("login/login.html.j2", data_incorrect=True)


@app.route("/logout")
def logout() -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    flask.session.pop("data")
    return flask.render_template("logout/logout.html.j2")


@app.route("/users", methods=["GET", "POST"])
def users() -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        users_data = get_request("/users")
        return flask.render_template("users/users.html.j2", users=users_data.json())
    elif flask.request.method == "POST":
        if "new" in flask.request.form:
            return flask.redirect(flask.url_for("user"))
        if "modify" in flask.request.form:
            return flask.redirect(flask.url_for("user", user_name=flask.request.form["username"]))
        if "delete" in flask.request.form:
            delete_request(f"/users/{flask.request.form['username']}")
            return flask.render_template("users/users.html.j2", users=get_request("/users").json())


@app.route("/users/user/", methods=["GET", "POST"])
@app.route("/users/user/<user_name>", methods=["GET", "POST"])
def user(user_name: str | None = None) -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        if user_name is None:
            return flask.render_template("users/user/user.html.j2", new=True)
        user_data = get_request(f"/users/{user_name}")
        if user_data.status_code != 200:
            return "There has been an error."
        return flask.render_template("users/user/user.html.j2", user_data=user_data.json())
    elif flask.request.method == "POST":
        if "new" in flask.request.form:
            data = {
                "username": flask.request.form["username"],
                "password": flask.request.form["password"],
                "email": flask.request.form["email"],
                "name": flask.request.form["first_name"],
                "last_name": flask.request.form["last_name"],
                "birthday": flask.request.form["birthday"]
            }
            post_request("/users", data)
            return flask.redirect(flask.url_for("users"))
        else:
            data = {
                "username": flask.request.form["username"],
                "email": flask.request.form["email"],
                "name": flask.request.form["first_name"],
                "last_name": flask.request.form["last_name"],
                "birthday": flask.request.form["birthday"]
            }
            put_request(f"/users/{user_name}", data)
            return flask.redirect(flask.url_for("users"))


@app.route("/students", methods=["GET", "POST"])
def students() -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        users: list[dict[str, int | str | dict[str, str]]] = get_request("/students").json()
        classes_data: list[dict[str, str | int]] = get_request("/school_classes").json()
        for i in range(len(users)):
            for class_data in classes_data:
                if class_data["id"] == users[i]["school_class_id"]:
                    users[i]["class_name"] = str(class_data["grade_id"]) + str(class_data["name"])
                    continue

        return flask.render_template("students/students.html.j2", students=users)
    elif flask.request.method == "POST":
        if "delete" in flask.request.form:
            ret = get_request("/users")
            for user in ret.json():
                if user["id"] == flask.request.form["id"]:
                    ret = delete_request(f"/users/{user['username']}/student")
                    print(ret.status_code)
                    users = get_request("/students").json()
                    return flask.render_template("students/students.html.j2", students=users)
        if "modify" in flask.request.form:
            ret = get_request("/users")
            for user in ret.json():
                if user["id"] == flask.request.form["id"]:
                    return app.redirect(flask.url_for("student", user_name=user["username"]))
            return "There has been an error."
        if "new" in flask.request.form:
            return app.redirect(flask.url_for("student"))


@app.route("/students/student/", methods=["GET", "POST"])
@app.route("/students/student/<user_name>", methods=["GET", "POST"])
def student(user_name: str | None = None) -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        classes_data = get_request("/school_classes").json()
        for i in range(len(classes_data)):
            classes_data[i]["class_name"] = str(classes_data[i]["grade_id"]) + classes_data[i]["name"]
        if user_name is None:
            return flask.render_template("students/student/student.html.j2", classesgit=classes_data)
        student_data = get_request(f"/users/{user_name}/student")
        if student_data.status_code != 200:
            return "There has been an error."
        return flask.render_template("students/student/student.html.j2", user_data=student_data.json(),
                                     classes=classes_data)
    elif flask.request.method == "POST":
        if flask.request.form["method"] == "new":
            post_request(f"/users/{user_name}/student")
        elif flask.request.form["method"] == "modify":
            pass


@app.route("/teachers", methods=["GET", "POST"])
def teachers() -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        users = get_request("/teachers")
        return flask.render_template("teachers/teachers.html.j2", users=users.json())
    elif flask.request.method == "POST":
        # TODO: Implement this
        pass


@app.route("/classes", methods=["GET", "POST"])
def classes() -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        school_classes = get_request("/school_classes")
        classes_data: list[dict[str, str | int]] = school_classes.json()
        for i in range(len(classes_data)):
            classes_data[i]["grade_id"] = str(classes_data[i]["grade_id"])
        return flask.render_template("classes/classes.html.j2", classes=classes_data)
    elif flask.request.method == "POST":
        if "new" in flask.request.form:
            # TODO: Implement this
            pass
        if "modify" in flask.request.form:
            # TODO: Implement this
            pass
        if "delete" in flask.request.form:
            # TODO: Implement this
            pass


@app.route("/class", methods=["GET", "POST"])
def class_() -> str | flask.Response:
    if "data" not in flask.session:
        return flask.redirect(flask.url_for("login"), code=401)
    if flask.request.method == "GET":
        return flask.render_template("classes/class/class.html.j2")
    elif flask.request.method == "POST":
        pass


if __name__ == "__main__":
    app.run(debug=True)
