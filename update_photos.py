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

def clean_old_entries():
    """Clean up photos that no longer exist in the photos directory"""
    # Get all photos from database
    photos = Photo.query.all()
    
    # Get all files in the photos directory
    existing_files = set(os.listdir(PHOTOS_DIR))
    
    # Find photos that no longer exist in the directory
    deleted_count = 0
    for photo in photos:
        if photo.filename not in existing_files:
            print(f"Removing database entry for missing file: {photo.filename}")
            db.session.delete(photo)
            deleted_count += 1
    
    if deleted_count > 0:
        db.session.commit()
        print(f"Removed {deleted_count} entries for missing files")
    else:
        print("No missing files to clean up")

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

def update_photos():
    """Update database with renamed photos"""
    admin = create_admin_if_not_exists()
    
    # First clean up old entries
    clean_old_entries()
    
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
            
        # Create thumbnail if it doesn't exist
        if create_thumbnail(filename):
            # Extract title from filename (remove extension)
            title = os.path.splitext(filename)[0]
            
            # Add to database
            new_photo = Photo(
                title=title,
                description="Updated photo",
                filename=filename,
                thumbnail=filename,
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
    update_photos()
    print("Completed. Your photos have been updated without duplicates.") 