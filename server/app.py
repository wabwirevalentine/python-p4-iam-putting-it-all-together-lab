#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import create_app
from models import User, Recipe

app, api, db, bcrypt = create_app()


class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        if not username or not password:
            return {'message': 'Username and password are required'}, 422

        try:
            user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )
            user.password_hash = password  # This will trigger the setter
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Username already exists'}, 422
        except ValueError as e:
            db.session.rollback()
            return {'message': str(e)}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'Not logged in'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        return user.to_dict(), 200


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {'message': 'Invalid username or password'}, 401


class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if user_id:  # Check if user_id exists and is truthy (not None)
            session.pop('user_id')
            return {}, 204
        return {'message': 'Not logged in'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:  # Check if user_id doesn't exist or is falsy (None, 0, etc.)
            return {'message': 'Not logged in'}, 401

        recipes = Recipe.query.all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:  # Check if user_id doesn't exist or is falsy
            return {'message': 'Not logged in'}, 401

        data = request.get_json()
        try:
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except:
            return {'message': 'Invalid recipe data'}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)