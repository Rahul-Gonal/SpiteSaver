from datetime import datetime
from flask_login import UserMixin
from .exts import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(5), primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    
    # Added relationships for easy querying
    goals = db.relationship('Goal', backref='user', lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")

class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(5), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)  # Added this flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    transactions = db.relationship('Transaction', backref='goal', lazy=True, cascade="all, delete-orphan")

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(5), db.ForeignKey('users.id'), nullable=False) # Added user link
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    tx_type = db.Column(db.String(10), nullable=False, default="save")  # 'save' or 'spend'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False, default="Spite Save") # Added desc
    tag = db.Column(db.String(100), nullable=True)
    is_milestone = db.Column(db.Boolean, default=False) # Tracks if this tx hit 100%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(uid):
    return User.query.get(str(uid))
