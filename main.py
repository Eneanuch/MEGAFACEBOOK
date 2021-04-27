import datetime
from werkzeug.utils import secure_filename
from data.db_session import global_init
from flask import url_for, Flask, render_template, send_from_directory, redirect, abort, request, session
from flask_ngrok import run_with_ngrok
from flask_restful import reqparse, abort, Api, Resource
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from json import loads
import os
from data import db_session, post_resources, user_resources
from data.users import User
from data.messages import Messages
from data.posts import Posts
from data.friends import Friends
from forms.user import RegisterForm, LoginForm
from forms.post import PostForm
from forms.posts_update import PostUpdateForm
from forms.message import MessageForm
from forms.profile_update import UpdateForm
from forms.profile_photo import PhotoForm
from forms.profile_password import PasswordForm
from forms.friend import FriendForm
import logging

SIDEBAR_PATH = 'data/configs/sidebar.json'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'svg',
                      'PNG', 'JPG', 'JPEG', 'GIF', 'SVG']


logging.basicConfig(filename='main.log',
                    format='%(levelname)s %(asctime)s %(message)s')

sidebar_elements = list()
parameters = {"title": "MEGAFACEBOOK", "sidebar": sidebar_elements}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'A231f1s9p23klbjt8'
# секретный ключ
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)  # время жизни сессии

# обозначение папок с загружаемыми файлами
app.config['UPLOAD_FOLDER_PROFILES'] = 'static/img/upload'
app.config['UPLOAD_FOLDER_POSTS'] = 'static/img/upload/posts'

# инициализация апи
api = Api(app)

# инициализация логин менеджера
login_manager = LoginManager()
login_manager.init_app(app)

logging.info('Loaded starter pack for app')

# run_with_ngrok(app)

logging.info('run with ngrok')
# запуск программы с ngrok


def main():
    # загружаем сайдбар
    load_sidebar_elem()
    logging.info('Loaded sidebar elements')
    # инициализация бд
    global_init("data/db/main.db")
    logging.info('Loaded database')

    # добавление апи
    api.add_resource(post_resources.PostsListResource, '/api/v2/posts')
    api.add_resource(post_resources.PostsResource, '/api/v2/posts/<int:post_id>')

    api.add_resource(user_resources.UserListResource, '/api/v2/users')
    api.add_resource(user_resources.UserResource, '/api/v2/users/<int:user_id>')

    logging.info('Loaded api')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    logging.info('App run!')


#  Регистрация нового пользователя
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
        # Добавление фотографии (сохраняется на сервере)
        f = form.photo.data
        filename = secure_filename(f.filename)
        db_sess = db_session.create_session()
        # В папке не должно быть файлов с одинаковыми названиями
        if db_sess.query(User).filter(User.photo == filename).first():
            parameters['form'] = form
            parameters['message'] = "Недопустимое имя файла. Переименуйте"
            return render_template('register.html', **parameters)
        if not allowed_file(filename):
            parameters['form'] = form
            parameters['message'] = "Загрузите корректное изображение"
            return render_template('register.html', **parameters)
        f.save(os.path.join(app.config['UPLOAD_FOLDER_PROFILES'], filename))

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


# Авторизация
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
@login_required
def main_page():
    db_sess = db_session.create_session()
    parameters['message'] = ""
    parameters['title'] = f"MEGAFACEBOOK: Главная"
    # Сортировка по дате
    parameters['posts'] = sorted(db_sess.query(Posts).all(), key=lambda x: x.date, reverse=True)

    return render_template("main_page.html", **parameters)


@app.route('/about')
def about():
    parameters['message'] = ""
    parameters['title'] = "MEGAFACEBOOK: О нас"
    return render_template("information.html", **parameters)


# Создание поста
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
        # Загрузка фотографии
        f = form.photo.data
        filename = secure_filename(f.filename)
        db_sess = db_session.create_session()
        if db_sess.query(Posts).filter(Posts.photo == filename).first():
            parameters['form'] = form
            parameters['message'] = "Недопустимое имя файла. Переименуйте"
            return render_template('post.html', **parameters)
        if not allowed_file(filename):
            parameters['form'] = form
            parameters['message'] = "Загрузите корректное изображение"
            return render_template('post.html', **parameters)
        f.save(os.path.join(app.config['UPLOAD_FOLDER_POSTS'], filename))

        post.photo = filename
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    parameters['title'] = 'Опубликовать пост'
    parameters['form'] = form
    return render_template('post.html', **parameters)


# Редактирование поста
@app.route('/posts/id<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    parameters['message'] = ""
    form = PostUpdateForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).filter(Posts.id == post_id, Posts.author == current_user.id).first()
        if post:
            form.text.data = post.text
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).filter(Posts.id == post_id, Posts.author == current_user.id).first()
        if post:
            post.text = form.text.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    parameters['title'] = 'Редактировать поста'
    parameters['form'] = form
    return render_template('post_update.html', **parameters)


# Удвление поста
@app.route('/posts_delete/id<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_delete(post_id):
    parameters['message'] = ""
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == post_id, Posts.author == current_user.id).first()
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


# Профиль пользователя
@app.route('/profiles/id<int:user_id>')
@login_required
def profile(user_id):
    parameters['message'] = ""
    db_sess = db_session.create_session()
    user1 = db_sess.query(User).filter(User.id == user_id).first()
    if not user1:
        abort(404)
    parameters['title'] = f"MEGAFACEBOOK: {user1.name} {user1.surname}"
    parameters['user'] = user1
    parameters['count_of_friends'] = len(list(db_sess.query(Friends).filter(
        (Friends.from_user == user1.id) | (Friends.to_user == user1.id),
        Friends.accepted == 1).all()))
    parameters['posts'] = db_sess.query(Posts).filter(Posts.author == user_id).all()
    return render_template("profile_page.html", **parameters)


# Изменение общей информации
@app.route('/profiles_update/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    parameters['message'] = ""
    parameters['title'] = 'Редактировать профиля'
    form = UpdateForm()
    parameters['form'] = form
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        if user:
            form.name.data = user.name
            form.surname.data = user.surname
            form.email.data = user.email
            form.phone.data = user.phone
            form.city.data = user.city
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        if db_sess.query(User).filter((User.email == form.email.data) | (User.phone == form.phone.data),
                                      User.id != current_user.id).first():
            parameters['form'] = form
            parameters['message'] = "Такой пользователь уже есть"
            return render_template('profile_update.html', **parameters)
        if user:
            user.name = form.name.data
            user.surname = form.surname.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.city = form.city.data
            db_sess.commit()
            return redirect(f'/profiles/id{current_user.id}')
        else:
            abort(404)
    return render_template('profile_update.html', **parameters)


# Изменение фотографии
@app.route('/profiles_photo/', methods=['GET', 'POST'])
@login_required
def edit_photo():
    parameters['message'] = ""
    parameters['title'] = 'Изменить аватарку'
    form = PhotoForm()
    parameters['form'] = form
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        if not user:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        f = form.photo.data
        filename = secure_filename(f.filename)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.photo == filename).first():
            parameters['form'] = form
            parameters['message'] = "Недопустимое имя файла. Переименуйте"
            return render_template('profile_photo.html', **parameters)
        if not allowed_file(filename):
            parameters['form'] = form
            parameters['message'] = "Загрузите корректное изображение"
            return render_template('profile_photo.html', **parameters)
        f.save(os.path.join(app.config['UPLOAD_FOLDER_PROFILES'], filename))
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        user.photo = filename
        db_sess.commit()
        return redirect(f'/profiles/id{current_user.id}')
    return render_template('profile_photo.html', **parameters)


# Изменение пароля
@app.route('/profiles_password/', methods=['GET', 'POST'])
@login_required
def edit_password():
    parameters['message'] = ""
    parameters['title'] = 'Изменить пароль'
    form = PasswordForm()
    parameters['form'] = form
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        if not user:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        # Запрашиваем старый пароль
        if not user.check_password(form.old.data):
            parameters['form'] = form
            parameters['message'] = "Неверный старый пароль"
            return render_template('profile_password.html', **parameters)
        if form.password.data != form.password_again.data:
            parameters['form'] = form
            parameters['message'] = "Пароли не совпадают"
            return render_template('profile_password.html', **parameters)
        if user:
            user.set_password(form.password.data)
            db_sess.commit()
        else:
            abort(404)
        return redirect(f'/profiles/id{current_user.id}')
    return render_template('profile_password.html', **parameters)


@app.route("/my_profile")
@login_required
def my_profile():
    parameters['message'] = ""
    return redirect(f'/profiles/id{current_user.id}')


@app.route("/friends", methods=['GET', 'POST'])
@login_required
def friends():
    parameters['title'] = "MEGAFACEBOOK: Друзья"
    parameters['message'] = ""
    form = FriendForm()
    parameters['form'] = form
    parameters['friends'] = list()
    if request.method == "GET":
        db_sess = db_session.create_session()
        friends_list = db_sess.query(Friends).filter(
            ((Friends.to_user == current_user.id) | (Friends.from_user == current_user.id)) & Friends.accepted)
        friends_user_list = list()
        for i in friends_list:
            friends_user_list.append(db_sess.query(User).filter(
                (i.to_user if i.to_user != current_user.id else i.from_user) == User.id).first())
        parameters['friends'] = friends_user_list
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        name = form.name.data
        result = db_sess.query(User).filter(User.name.like(f"%{name}%")
                                            | User.surname.like(f"%{name}%")
                                            | User.city.like(f"%{name}%"), User.id != current_user.id).all()
        parameters['friends_find'] = result
        return render_template("friends.html", **parameters)
    return render_template("friends.html", **parameters)


@app.route("/add_friend/id<int:user_id>")
@login_required
def add_friend(user_id):
    parameters['title'] = "MEGAFACEBOOK: Добавление друга"
    parameters['message'] = ""
    from_user_id = current_user.id
    to_user_id = user_id
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


@app.route("/delete_friend/id<int:user_id>")
@login_required
def delete_friend(user_id):
    parameters['title'] = "MEGAFACEBOOK: Удаление друга"
    parameters['message'] = ""
    db_sess = db_session.create_session()
    friend = db_sess.query(Friends).filter((Friends.from_user == user_id)
                                           | (Friends.to_user == user_id),
                                           (Friends.from_user == current_user.id)
                                           | (Friends.to_user == current_user.id)).first()
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


# Все сообщения
@app.route('/messages')
@login_required
def messages():
    parameters['message'] = ""
    parameters['title'] = "MEGAFACEBOOK: Сообщения"
    db_sess = db_session.create_session()
    messages_list = sorted(db_sess.query(Messages).filter((Messages.from_user == current_user.id)
                                                          | (Messages.to_user == current_user.id)).all(),
                           key=lambda x: x.date, reverse=True)
    friends_list = sorted(db_sess.query(Friends).filter(((Friends.from_user == current_user.id)
                                                         | (Friends.to_user == current_user.id)),
                                                        Friends.accepted == True).all(), key=lambda x: x.date,
                          reverse=True)
    friends_from_me = sorted(db_sess.query(Friends).filter(Friends.from_user == current_user.id).all(),
                             key=lambda x: x.date, reverse=True)
    friends_to_me = sorted(db_sess.query(Friends).filter(Friends.to_user == current_user.id).all(),
                           key=lambda x: x.date, reverse=True)
    users = [return_not_me(i.from_user, i.to_user) for i in messages_list] + \
            [return_not_me(i.from_user, i.to_user) for i in friends_list] + \
            [return_not_me(i.from_user, i.to_user) for i in friends_from_me] + \
            [return_not_me(i.from_user, i.to_user) for i in friends_to_me]
    users_new = list()
    for i in users:
        if i not in users_new:
            users_new.append(i)
    users_real = list()

    for i in users_new:
        users_real.append(db_sess.query(User).filter(User.id == i).first())

    parameters['users'] = users_real
    return render_template('messages.html', **parameters)


# Диалоги
@app.route('/messages/id<int:user_id>', methods=['GET', 'POST'])
@login_required
def messages_with_user(user_id):
    form = MessageForm()
    parameters['message'] = ""
    parameters['title'] = "MEGAFACEBOOK: Переписка"
    db_sess = db_session.create_session()

    your_messages = db_sess.query(Messages).filter(Messages.from_user == current_user.id, Messages.to_user == user_id).all()
    pen_friend_messages = db_sess.query(Messages).filter(Messages.from_user == user_id,
                                                         Messages.to_user == current_user.id).all()
    if current_user.id == user_id:
        pen_friend_messages = []
    all_messages = your_messages + pen_friend_messages
    all_messages = sorted(all_messages, key=lambda x: x.date)
    parameters['all_messages'] = all_messages

    pen_friend = db_sess.query(User).filter(User.id == user_id).first()

    parameters['pen_friend'] = pen_friend
    parameters['form'] = form

    if request.method == 'POST':
        message = Messages(
            from_user=current_user.id,
            to_user=user_id,
            text=form.message.data
        )
        db_sess.add(message)
        db_sess.commit()
        return redirect(f'/messages/id{user_id}')

    return render_template('message_page.html', **parameters)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Обработка ошибок
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


def return_not_me(user_id, id2):
    return user_id if current_user.id != user_id else id2


def load_sidebar_elem():
    global sidebar_elements
    with open(SIDEBAR_PATH, "rt", encoding="utf8") as f:
        sidebar_elements = loads(f.read())
        parameters['sidebar'] = sidebar_elements


if __name__ == '__main__':
    main()
