from managers import FuncManager, DBManager, TranslateManager
from flask import url_for, Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/main")
def main_page():
    return render_template("main_page.html")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
