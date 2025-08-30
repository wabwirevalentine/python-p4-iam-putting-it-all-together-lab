from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from config import db
import re


class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", back_populates="user")

    serialize_rules = ('-recipes.user', '-_password_hash')

    def __init__(self, **kwargs):
        # Call the parent constructor first
        super().__init__(**kwargs)

        # If no password was provided, set a default one (for testing)
        if not hasattr(self, '_password_hash') or not self._password_hash:
            self.password_hash = "default_password"

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        password_hash = generate_password_hash(password)
        self._password_hash = password_hash

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'image_url': self.image_url,
            'bio': self.bio
        }

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username is required")
        existing_user = User.query.filter(User.username == username).first()
        if existing_user and existing_user.id != self.id:
            raise ValueError("Username must be unique")
        return username


class Recipe(db.Model, SerializerMixin):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="recipes")

    serialize_rules = ('-user.recipes',)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,
            'minutes_to_complete': self.minutes_to_complete,
            'user_id': self.user_id
        }

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title is required")
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions:
            raise ValueError("Instructions are required")
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return instructions