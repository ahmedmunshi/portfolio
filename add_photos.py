import os
import sys
from datetime import datetime
from PIL import Image
from app import create_app, db
from app.models import User, Photo

# Create Flask app context
app = create_app()
app.app_context().push()

# Configuration
PHOTOS_DIR = 'app/static/images/photos'
THUMBNAILS_DIR = 'app/static/images/thumbnails'
THUMBNAIL_SIZE = (400, 400)

def create_admin_if_not_exists():
    """Create admin user if doesn't exist"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin')  # Default password, change this!
        db.session.add(admin)
        db.session.commit()
        print("Created admin user with password: admin")
    return admin

def create_thumbnail(filename):
    """Create thumbnail for image"""
    img_path = os.path.join(PHOTOS_DIR, filename)
    thumb_path = os.path.join(THUMBNAILS_DIR, filename)
    
    try:
        img = Image.open(img_path)
        img.thumbnail(THUMBNAIL_SIZE)
        img.save(thumb_path)
        return True
    except Exception as e:
        print(f"Error creating thumbnail for {filename}: {e}")
        return False

def add_photos_to_db():
    """Add photos from directory to database"""
    admin = create_admin_if_not_exists()
    
    # Get all files in photos directory
    photo_files = os.listdir(PHOTOS_DIR)
    photo_files = [f for f in photo_files if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
    
    # Get existing photos in database
    existing_photos = Photo.query.all()
    existing_filenames = [photo.filename for photo in existing_photos]
    
    added_count = 0
    
    for filename in photo_files:
        if filename in existing_filenames:
            print(f"Photo {filename} already in database, skipping")
            continue
            
        # Get image dimensions (but don't save to db yet - need migration)
        img_path = os.path.join(PHOTOS_DIR, filename)
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                print(f"Image dimensions: {width}x{height} (not saved to DB)")
        except Exception as e:
            print(f"Error getting dimensions for {filename}: {e}")
            
        # Create thumbnail
        if create_thumbnail(filename):
            # Add to database
            new_photo = Photo(
                title=os.path.splitext(filename)[0],
                description="Added automatically",
                filename=filename,
                thumbnail=filename,
                # width=width,  # Commented out until migration
                # height=height,  # Commented out until migration
                user_id=admin.id,
                featured=True  # Make all photos featured by default
            )
            
            db.session.add(new_photo)
            added_count += 1
    
    if added_count > 0:
        db.session.commit()
        print(f"Added {added_count} new photos to database")
    else:
        print("No new photos to add")

if __name__ == '__main__':
    add_photos_to_db()
    print("Completed. You can now view photos on the website.") 