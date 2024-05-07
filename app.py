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


if __name__ == "__main__":
    app.run(debug=True)
