import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # Fix for Postgres URI format on Render (if applicable)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings to prevent auth issues
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # Secure only in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload settings
    # For production on Render with persistent storage
    IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
    
    if IS_PRODUCTION and os.environ.get('RENDER_PERSISTENT_STORAGE_DIR'):
        # Use Render persistent storage if available
        UPLOAD_FOLDER = os.path.join(os.environ.get('RENDER_PERSISTENT_STORAGE_DIR'), 'photos')
        THUMBNAIL_FOLDER = os.path.join(os.environ.get('RENDER_PERSISTENT_STORAGE_DIR'), 'thumbnails')
    else:
        # Local development paths
        UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images/photos')
        THUMBNAIL_FOLDER = os.path.join(basedir, 'app/static/images/thumbnails')
    
    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
    
    # Image settings
    THUMBNAIL_SIZE = (800, 800)
    MAX_IMAGE_SIZE = (2000, 2000)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size
    
    # Admin settings
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin' 