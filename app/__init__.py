import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'change-this-secret'
    # sqlite file in project root
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # import models so that tables can be created
    from . import models

    with app.app_context():
        # create some default branches if none exist
        db.create_all()
        from .models import Branch
        if Branch.query.count() == 0:
            b1 = Branch(name='الفرع الرئيسي', location='المدينة')
            b2 = Branch(name='فرع صلالة', location='صلالة')
            db.session.add_all([b1, b2])
            db.session.commit()

    # register routes
    from .routes import bp
    app.register_blueprint(bp)

    return app
