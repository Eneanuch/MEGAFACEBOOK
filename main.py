from managers import FuncManager, DBManager, TranslateManager
from flask import url_for, Flask, render_template
from json import loads

app = Flask(__name__)

sidebar_elements = list()

parameters = {"title": "MEGAFACEBOOK", "sidebar": sidebar_elements}


@app.route("/")
@app.route("/main")
def main_page():
    parameters['title'] = f"MEGAFACEBOOK: Главная"
    return render_template("main_page.html", **parameters)


@app.errorhandler(400)
@app.errorhandler(404)
def handle_bad_request(e):
    parameters['title'] = f"MEGAFACEBOOK: Error {e}"
    return render_template("error.html", error=e.name, **parameters)


def load_sidebar_elem():
    global sidebar_elements
    with open("data/sidebar.json", "rt", encoding="utf8") as f:
        sidebar_elements = loads(f.read())
        parameters['sidebar'] = sidebar_elements


if __name__ == '__main__':
    load_sidebar_elem()
    app.run(port=8080, host='127.0.0.1')
