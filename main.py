from managers import FuncManager, DBManager, TranslateManager
from flask import url_for, Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/main")
def main_page():
    return render_template("main_page.html")


@app.errorhandler(400)
@app.errorhandler(404)
def handle_bad_request(e):
    return render_template("error.html", error=e.name)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
