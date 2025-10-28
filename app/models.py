from . import db
from datetime import date

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(256))

    clients = db.relationship('Client', backref='branch', lazy=True)

    def __repr__(self):
        return f'<Branch {self.name}>'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)

    reports = db.relationship('ValuationReport', backref='client', lazy=True)

    def __repr__(self):
        return f'<Client {self.name}>'

class ValuationReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_number = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    date = db.Column(db.Date, default=date.today)
    note = db.Column(db.Text)
    employee_name = db.Column(db.String(200))

    def __repr__(self):
        return f'<ValuationReport {self.report_number}>'
