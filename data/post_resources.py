from flask_restful import Resource, reqparse
from flask import abort, jsonify
from data import db_session
from .posts import Posts
from datetime import datetime


parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('author', required=True, type=int)
parser.add_argument('text', required=True)
parser.add_argument('photo', required=True)
parser.add_argument('date', required=True)


def abort_if_posts_not_found(post_id):
    session = db_session.create_session()
    posts = session.query(Posts).get(post_id)
    if not posts:
        abort(404)


class PostsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        posts = session.query(Posts).all()
        return jsonify({'posts': [item.to_dict(
            only=('id', 'author', 'photo',
                  'text', 'date')) for item in posts]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        posts = Posts(
            id=args['id'],
            author=args['author'],
            text=args['text'],
            photo=args['photo'],
            date=datetime.strptime(args['date'], '%y-%m-%d %H:%M:%S')
        )
        session.add(posts)
        session.commit()
        return jsonify({'success': 'OK'})


class PostsResource(Resource):
    def get(self, post_id):
        abort_if_posts_not_found(post_id)
        session = db_session.create_session()
        posts = session.query(Posts).get(post_id)
        return jsonify({'posts': posts.to_dict(
            only=('id', 'author', 'photo',
                  'text', 'date'))})

    def delete(self, post_id):
        abort_if_posts_not_found(post_id)
        session = db_session.create_session()
        posts = session.query(Posts).get(post_id)
        session.delete(posts)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, post_id):
        args = parser.parse_args()
        abort_if_posts_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Posts).get(post_id)
        if session.query(Posts).get(args['id']):
            return jsonify({'error': 'Have same post'})
        post.id = args['id']
        post.text = args['text']
        post.photo = args['photo']
        post.date = datetime.strptime(args['date'], '%y-%m-%d %H:%M:%S')
        session.commit()
        return jsonify({'success': 'OK'})