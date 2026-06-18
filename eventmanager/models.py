from . import db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    
    first_name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    
    email = db.Column(db.String(100), unique=True)
    
    password_hash = db.Column(db.String(255))
    
    phone = db.Column(db.String(20))
    
    address = db.Column(db.String(200))
    
    events = db.relationship('Event', backref='organizer', foreign_keys='Event.user_id', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='user', foreign_keys='Booking.user_id', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', foreign_keys='Comment.user_id', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    title = db.Column(db.String(100), nullable=False)
    
    description = db.Column(db.Text)
    
    category = db.Column(db.String(50))
    
    location = db.Column(db.String(100))
    
    date = db.Column(db.DateTime, nullable=False)
    
    price = db.Column(db.Float)
    
    tickets_available = db.Column(db.Integer)
    
    image = db.Column(db.String(200))
    
    status = db.Column(db.String(20), default='Open')
    
    acknowledgement_type = db.Column(db.String(20), default='None')
    
    acknowledgement_text = db.Column(db.Text)
    
    acknowledgement_location = db.Column(db.String(100))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    bookings = db.relationship('Booking', backref='event', foreign_keys='Booking.event_id', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='event', foreign_keys='Comment.event_id', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Event {self.title}>'


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    total_price = db.Column(db.Float)
    
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def __repr__(self):
        return f'<Booking {self.order_id}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    text = db.Column(db.Text, nullable=False)
    
    comment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'
