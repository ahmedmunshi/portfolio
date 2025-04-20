from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

# Association table for many-to-many relationship between photos and categories
photo_category = db.Table('photo_category',
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    photos = db.relationship('Photo', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    filename = db.Column(db.String(120), index=True, unique=True)
    thumbnail = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    featured = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Image dimensions - commented out until migration is run
    # width = db.Column(db.Integer)
    # height = db.Column(db.Integer)
    
    # EXIF data
    camera_model = db.Column(db.String(100))
    lens_model = db.Column(db.String(100))
    focal_length = db.Column(db.String(20))
    exposure_time = db.Column(db.String(20))
    aperture = db.Column(db.String(20))
    iso = db.Column(db.String(20))
    date_taken = db.Column(db.DateTime)
    
    # Many-to-many relationship with categories
    categories = db.relationship('Category', secondary=photo_category,
                               backref=db.backref('photos', lazy='dynamic'))

    def __repr__(self):
        return f'<Photo {self.title}>'
    
    @property
    def photo_url(self):
        return f'/static/images/photos/{self.filename}'
    
    @property
    def thumbnail_url(self):
        return f'/static/images/thumbnails/{self.thumbnail}'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    slug = db.Column(db.String(64), index=True, unique=True)
    
    def __repr__(self):
        return f'<Category {self.name}>' 