from flask import jsonify, request, Blueprint
from . import db_session
from .users import User
from datetime import datetime

blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users', methods=['GET'])
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'name', 'surname', 'photo',
                                    'email', 'phone', 'city', 'hashed_password',
                                    'registration_date', 'birthday')) for item in users]
        }
    )


@blueprint.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id == id).all()
    if not users:
        return jsonify({'error': "Not Found"})
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'name', 'surname', 'photo',
                                    'email', 'phone', 'city', 'hashed_password',
                                    'registration_date', 'birthday')) for item in users]
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def add_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'name', 'surname', 'photo',
                  'email', 'phone', 'city', 'hashed_password',
                  'registration_date', 'birthday']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = User(
        id=request.json['id'],
        name=request.json['name'],
        surname=request.json['surname'],
        photo=request.json['photo'],
        email=request.json['email'],
        phone=request.json['phone'],
        city=request.json['city'],
        hashed_password=request.json['hashed_password'],
        registration_date=datetime.strptime(request.json['registration_date'],
                                            '%y-%m-%d %H:%M:%S'),
        birthday=datetime.strptime(request.json['birthday'], '%y-%m-%d %H:%M:%S')
    )
    if db_sess.query(User).filter(User.id == request.json['id']).all():
        return jsonify({'error': 'Id already exists'})
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route("/api/users/<int:id>", methods=['DELETE'])
def delete_user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user:
        return jsonify({'error': '404 Not Found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route("/api/users/<int:id>", methods=['PUT'])
def edit_user(id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'name', 'surname', 'photo',
                  'email', 'phone', 'city', 'hashed_password',
                  'registration_date', 'birthday']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user:
        return jsonify({'error': '404 Not Found'})
    if db_sess.query(User).filter(User.id == request.json['id']
                                  | User.email == request.json['email']
                                  | User.phone == request.json['phone']
                                  ).first():
        return jsonify({'error': 'User is not unique'})
    user.id = request.json['id']
    user.name = request.json['name']
    user.surname = request.json['surname']
    user.photo = request.json['photo']
    user.email = request.json['email']
    user.phone = request.json['phone']
    user.city = request.json['city']
    user.hashed_password = request.json['hashed_password']
    user.registration_date = datetime.strptime(request.json['registration_date'],
                                               '%y-%m-%d %H:%M:%S')
    user.birthday = datetime.strptime(request.json['birthday'], '%y-%m-%d %H:%M:%S')
    db_sess.commit()
    return jsonify({'success': 'OK'})
