from flask_restful import Resource, reqparse
from flask import abort, jsonify
from data import db_session
from .users import User
from datetime import datetime


parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('name', required=True)
parser.add_argument('surname', required=True)
parser.add_argument('photo', required=True)
parser.add_argument('email', required=True)
parser.add_argument('phone', required=True)
parser.add_argument('city', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('registration_date', required=True)
parser.add_argument('birthday', required=True)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    posts = session.query(User).get(user_id)
    if not posts:
        abort(404)


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'name', 'surname', 'photo',
                  'email', 'phone', 'city', 'hashed_password',
                  'registration_date', 'birthday')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            id=args['id'],
            name=args['name'],
            surname=args['surname'],
            photo=args['photo'],
            email=args['email'],
            phone=args['phone'],
            city=args['city'],
            hashed_password=args['hashed_password'],
            registration_date=datetime.strptime( args['registration_date'],
                                                 '%y-%m-%d %H:%M:%S'),
            birthday=datetime.strptime(args['birthday'], '%y-%m-%d %H:%M:%S')
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        posts = session.query(User).get(user_id)
        return jsonify({'users': posts.to_dict(
            only=('id', 'name', 'surname', 'photo',
                  'email', 'phone', 'city', 'hashed_password',
                  'registration_date', 'birthday'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        posts = session.query(User).get(user_id)
        session.delete(posts)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        args = parser.parse_args()
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if session.query(user_id).get(args['id']):
            return jsonify({'error': 'Have same user'})
        user.id = args['id']
        user.name = args['name']
        user.surname = args['surname']
        user.photo = args['photo']
        user.email = args['email']
        user.phone = args['phone']
        user.city = args['city']
        user.hashed_password = args['hashed_password']
        user.registration_date = datetime.strptime(args['registration_date'],
                                                   '%y-%m-%d %H:%M:%S')
        user.birthday = datetime.strptime(args['birthday'], '%y-%m-%d %H:%M:%S')
        session.commit()
        return jsonify({'success': 'OK'})
