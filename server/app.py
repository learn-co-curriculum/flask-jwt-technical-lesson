#!/usr/bin/env python3

from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema

@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login'
    ]

    if (request.endpoint) not in open_access_list and (not session.get('user_id')):
        return {'errors': ['401 Unauthorized']}, 401

class Signup(Resource):
    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')
        image_url = request_json.get('image_url')
        bio = request_json.get('bio')

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        user.password_hash = password
        
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return UserSchema().dump(user), 201
        except IntegrityError:
            return {'errors': ['422 Unprocessable Entity']}, 422

class CheckSession(Resource):
    def get(self):

        user = User.query.filter(User.id == session['user_id']).first()
        
        return UserSchema().dump(user), 200


class Login(Resource):
    def post(self):

        username = request.get_json()['username']
        password = request.get_json()['password']

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        return {'errors': ['401 Unauthorized']}, 401

class Logout(Resource):
    def delete(self):

        session['user_id'] = None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        recipes = [RecipeSchema().dump(r) for r in Recipe.query.all()]

        return recipes, 200

    def post(self):
        request_json = request.get_json()

        recipe = Recipe(
            title=request_json.get('title'),
            instructions=request_json.get('instructions'),
            minutes_to_complete=request_json.get('minutes_to_complete'),
            user_id=session['user_id']
        )

        try:
            db.session.add(recipe)
            db.session.commit()
            return RecipeSchema().dump(recipe), 201

        except IntegrityError:
            return {'errors': ['422 Unprocessable Entity']}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)