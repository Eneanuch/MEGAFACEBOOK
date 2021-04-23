import datetime

from data.db_session import global_init
from managers import FuncManager, DBManager, TranslateManager
from flask import url_for, Flask, render_template, send_from_directory, redirect, abort, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from json import loads
import os

from data import db_session
from data.users import User
from data.messages import Messages
from data.posts import Posts
from data.friends import Friends
from forms.user import RegisterForm, LoginForm
from forms.post import PostForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'A231f1s9p23klbjt8'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)

sidebar_elements = list()

parameters = {"title": "MEGAFACEBOOK", "sidebar": sidebar_elements}


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    parameters['title'] = "MEGAFACEBOOK: Регистрация"
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            parameters['form'] = form
            parameters['message'] = "Пароли не совпадают"
            return render_template('register.html', **parameters)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter((User.email == form.email.data) | (User.phone == form.phone.data)).first():
            parameters['form'] = form
            parameters['message'] = "Такой пользователь уже есть"
            return render_template('register.html', **parameters)
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            phone=form.phone.data,
            birthday=form.birthday.data,
            city=form.city.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    parameters['form'] = form
    return render_template('register.html', **parameters)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    parameters['title'] = "MEGAFACEBOOK: Авторизация"
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        parameters['message'] = "Неправильный логин или пароль"
        parameters["form"] = form
        return render_template('login.html',
                               **parameters)
    parameters["form"] = form
    return render_template('login.html', **parameters)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
@app.route("/main")
def main_page():
    parameters['title'] = f"MEGAFACEBOOK: Главная"
    return render_template("main_page.html", **parameters)


@app.errorhandler(400)
@app.errorhandler(404)
def handle_bad_request(e):
    parameters['title'] = f"MEGAFACEBOOK: Error {e.name}"
    return render_template("error.html", error=e.name, **parameters)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'static/favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/about')
def about():
    parameters['title'] = "MEGAFACEBOOK: О нас"
    return render_template("information.html", **parameters)


@app.route('/help')
def help_page():
    parameters['title'] = "MEGAFACEBOOK: Помощь"
    return render_template("help.html", **parameters)


def load_sidebar_elem():
    global sidebar_elements
    with open("data/sidebar.json", "rt", encoding="utf8") as f:
        sidebar_elements = loads(f.read())
        parameters['sidebar'] = sidebar_elements
        

@app.route('/posts', methods=['GET', 'POST'])
@login_required
def add_news():
    form = PostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Posts()
        post.text = form.text.data
        post.author = current_user.id
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    parameters['title'] = 'Опубликовать пост'
    parameters['form'] = form
    return render_template('post.html', **parameters)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = PostForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).filter(Posts.id == id, Posts.author == current_user.id).first()
        if post:
            form.text.data = post.text
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).filter(Posts.id == id, Posts.author == current_user.id).first()
        if post:
            post.text = form.text.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    parameters['title'] = 'Редактировать поста'
    parameters['form'] = form
    return render_template('post.html', **parameters)


@app.route('/posts_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id, Posts.author == current_user.id).first()
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    global_init("data/db/main.db")
    load_sidebar_elem()
    app.run(port=8080, host='127.0.1.1')


if __name__ == '__main__':
    main()