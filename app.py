import flask


app = flask.Flask(__name__)


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
        if username == "arne" and password == "1234":
            return flask.redirect(flask.url_for("home"))


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
            return app.redirect(flask.url_for("new"))


@app.route("/students/modify/<student_id>")
def modify_student(student_id: str):
    if flask.request.method == "GET":
        return "student " + student_id


@app.route("/students/new", methods=["GET", "POST"])
def new():
    if flask.request.method == "GET":
        return "new"


if __name__ == "__main__":
    app.run(debug=True)
