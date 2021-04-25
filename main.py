import datetime
from werkzeug.utils import secure_filename
from data.db_session import global_init
from managers import FuncManager, DBManager, TranslateManager
from flask import url_for, Flask, render_template, send_from_directory, redirect, abort, request, session
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
from forms.message import MessageForm

sidebar_elements = list()
parameters = {"title": "MEGAFACEBOOK", "sidebar": sidebar_elements}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'A231f1s9p23klbjt8'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = 'static/img/upload'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    load_sidebar_elem()
    global_init("data/db/main.db")
    app.run(port=8080, host='127.0.1.1')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    parameters['message'] = ""
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

        f = form.photo.data
        filename = secure_filename(f.filename)
        if not allowed_file(filename):
            parameters['form'] = form
            parameters['message'] = "Загрузите корректное изображение"
            return render_template('register.html', **parameters)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        user = User(
            name=form.name.data,
            surname=form.surname.data,
            photo=filename,
            email=form.email.data,
            phone=form.phone.data,
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
    parameters['message'] = ""
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
    parameters['message'] = ""
    parameters['title'] = f"MEGAFACEBOOK: Главная"
    return render_template("main_page.html", **parameters)


@app.route('/about')
def about():
    parameters['message'] = ""
    parameters['title'] = "MEGAFACEBOOK: О нас"
    return render_template("information.html", **parameters)


@app.route('/help')
def help_page():
    parameters['message'] = ""
    parameters['title'] = "MEGAFACEBOOK: Помощь"
    return render_template("help.html", **parameters)


@app.route('/posts', methods=['GET', 'POST'])
@login_required
def add_news():
    parameters['message'] = ""
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
    parameters['message'] = ""
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
    parameters['message'] = ""
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id, Posts.author == current_user.id).first()
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/profiles/id<int:id>')
@login_required
def profile(id):
    parameters['message'] = ""
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    parameters['title'] = f"MEGAFACEBOOK: {user.name} {user.surname}"
    parameters['user'] = user
    return render_template("profile_page.html", **parameters)


@app.route("/my_profile")
@login_required
def my_profile():
    parameters['message'] = ""
    return redirect(f'/profiles/id{current_user.id}')


@app.route("/friends")
@login_required
def friends():
    parameters['title'] = "MEGAFACEBOOK: Друзья"
    parameters['message'] = ""
    db_sess = db_session.create_session()
    friends_list = db_sess.query(Friends).filter(
        ((Friends.to_user == current_user.id) | (Friends.from_user == current_user.id)) & Friends.accepted)
    friends_user_list = list()
    for i in friends_list:
        friends_user_list.append(db_sess.query(User).filter(
            (i.to_user if i.to_user != current_user.id else i.from_user) == User.id).first())
    parameters['friends'] = friends_user_list
    return render_template("friends.html", **parameters)


@app.route("/add_friend/id<int:id>")
@login_required
def add_friend(id):
    parameters['title'] = "MEGAFACEBOOK: Добавление друга"
    parameters['message'] = ""
    from_user_id = current_user.id
    to_user_id = id
    db_sess = db_session.create_session()
    parameters['user'] = db_sess.query(User).filter(User.id == to_user_id).first()
    # проверка на себя же :)
    if from_user_id != to_user_id:

        same_friends = db_sess.query(Friends).filter(Friends.from_user == from_user_id,
                                                     Friends.to_user == to_user_id).first()
        if same_friends:
            # если уже была заявка
            parameters['message'] = "Вы уже отправили заявку в друзья этому пользователю"
            return render_template("profile_page.html", **parameters)
        same_friends2 = db_sess.query(Friends).filter(Friends.to_user == from_user_id,
                                                      Friends.from_user == to_user_id).first()
        # если была заявка от этого же пользователя
        friends = Friends(from_user=from_user_id, to_user=to_user_id)
        if same_friends2:
            # обновляем в бд данные о дружбе :)
            same_friends2.accepted = True
            db_sess.commit()
            parameters['message'] = "Теперь вы друзья"
            return render_template("profile_page.html", **parameters)
        # если пользователь отправил другому заявку
        db_sess.add(friends)
        db_sess.commit()
        parameters['message'] = "Заявка отправлена"
        return render_template("profile_page.html", **parameters)
    else:
        parameters['message'] = "Вы не можете добавить самого себя в друзья"
        return render_template("profile_page.html", **parameters)


@app.route("/delete_friend/id<int:id>")
@login_required
def delete_friend(id):
    parameters['title'] = "MEGAFACEBOOK: Удаление друга"
    parameters['message'] = ""
    db_sess = db_session.create_session()
    friend = db_sess.query(Friends).filter((Friends.from_user == id) | (Friends.to_user == id)).first()
    if friend:
        db_sess.delete(friend)
    db_sess.commit()
    return redirect("/friends")


@app.route("/requests")
@login_required
def friend_requests():
    parameters['title'] = "MEGAFACEBOOK: Заявки в друзья"
    parameters['message'] = ""
    db_sess = db_session.create_session()
    request_from = db_sess.query(Friends).filter(
        Friends.to_user == current_user.id, Friends.accepted == False
    ).all()
    request_to = db_sess.query(Friends).filter(
        Friends.from_user == current_user.id, Friends.accepted == False
    ).all()
    requests_to_user = list()
    for i in request_to:
        requests_to_user.append(db_sess.query(User).filter(
            i.to_user == User.id).first())
    requests_from_user = list()
    for i in request_from:
        requests_from_user.append(db_sess.query(User).filter(
            i.from_user == User.id).first())
    # print(requests_from_user, requests_to_user)
    parameters['requests_from'] = requests_from_user
    parameters['requests_to'] = requests_to_user
    return render_template("requests.html", **parameters)


@app.route('/messages')
@login_required
def messages():
    parameters['message'] = ""
    parameters['title'] = "MEGAFACEBOOK: Сообщения"
    db_sess = db_session.create_session()
    messages = db_sess.query(Messages).filter((Messages.from_user == current_user.id)
                                              | (Messages.to_user == current_user.id))
    new_messages = list()
    #for i in messages:
     #   if
     #   new_messages.append()
    return render_template('messages.html', **parameters)


@app.route('/messages/id<int:id>', methods=['GET', 'POST'])
@login_required
def messages_with_user(id):
    form = MessageForm()
    parameters['message'] = ""
    parameters['title'] = "MEGAFACEBOOK: Переписка"
    db_sess = db_session.create_session()

    your_messages = db_sess.query(Messages).filter(Messages.from_user == current_user.id, Messages.to_user == id).all()
    pen_friend_messages = db_sess.query(Messages).filter(Messages.from_user == id,                                         Messages.to_user == current_user.id).all()
    if current_user.id == id:
        pen_friend_messages = []
    all_messages = your_messages + pen_friend_messages
    all_messages = sorted(all_messages, key=lambda x: x.date)
    parameters['all_messages'] = all_messages

    pen_friend = db_sess.query(User).filter(User.id == id).first()

    parameters['pen_friend'] = pen_friend
    parameters['form'] = form

    if request.method == 'POST':
        message = Messages(
            from_user=current_user.id,
            to_user=id,
            text=form.message.data
        )
        db_sess.add(message)
        db_sess.commit()
        return redirect(f'/messages/id{id}')

    return render_template('message_page.html', **parameters)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.errorhandler(500)
@app.errorhandler(400)
@app.errorhandler(404)
def handle_bad_request(e):
    parameters['message'] = ""
    parameters['title'] = f"MEGAFACEBOOK: Error {e.name}"
    parameters['error'] = e.name
    return render_template("error.html", **parameters)


@app.errorhandler(401)
def unauthorized(e):
    parameters['message'] = ""
    parameters['title'] = f"MEGAFACEBOOK: Unauthorized"
    parameters['error'] = e.name
    return render_template("unauthorized.html", **parameters)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'static/favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


def load_sidebar_elem():
    global sidebar_elements
    with open("data/sidebar.json", "rt", encoding="utf8") as f:
        sidebar_elements = loads(f.read())
        parameters['sidebar'] = sidebar_elements


if __name__ == '__main__':
    main()
