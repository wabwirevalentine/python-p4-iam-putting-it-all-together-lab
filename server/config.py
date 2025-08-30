from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Define metadata naming convention (helps with migrations)
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Create db instance without app
db = SQLAlchemy(metadata=metadata)

def create_app():
    app = Flask(__name__)
    app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.json.compact = False

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    bcrypt = Bcrypt(app)
    api = Api(app)

    return app, api, db, bcrypt
