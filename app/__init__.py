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
        # create tables
        db.create_all()
        # lightweight auto-migration for new columns (SQLite only)
        try:
            from sqlalchemy import inspect
            from .models import ValuationReport
            inspector = inspect(db.engine)
            cols = {c['name'] for c in inspector.get_columns('valuation_report')}
            if 'employee_name' not in cols:
                # SQLite supports ALTER TABLE ADD COLUMN without defaults
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE valuation_report ADD COLUMN employee_name VARCHAR(200)'))
        except Exception:
            # best-effort; ignore if not applicable or already applied
            pass
        # create some default branches if none exist
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
