from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class PricedItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skin_quality = db.Column(db.String(64))
    skin_name = db.Column(db.String(64))
    weapon_name = db.Column(db.String(64))
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)

    def get(self, value):
        if value == 'weapon_name':
            return self.weapon_name
        elif value == 'skin_quality':
            return self.skin_quality
        elif value == 'skin_name':
            return self.skin_name
        elif value == 'min_price':
            return self.min_price
        elif value == 'max_price':
            return self.max_price

    def __repr__(self):
        return f'{self.skin_quality} {self.weapon_name} {self.skin_name}, minimum price {self.min_price}, maximum price {self.max_price}'


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skin_quality = db.Column(db.String(64))
    skin_name = db.Column(db.String(64))
    weapon_name = db.Column(db.String(64))
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    timestamp = db.Column(db.String(64))

    def get(self, value):
        if value == 'weapon_name':
            return self.weapon_name
        elif value == 'skin_quality':
            return self.skin_quality
        elif value == 'skin_name':
            return self.skin_name
        elif value == 'min_price':
            return self.min_price
        elif value == 'max_price':
            return self.max_price
        elif value == 'timestamp':
            return self.timestamp

    def __repr__(self):
        return f'{self.skin_quality} {self.weapon_name} {self.skin_name}, minimum price {self.min_price}, maximum price {self.max_price}, scanned at {self.timestamp}'