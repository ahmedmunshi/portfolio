import os
from PIL import Image
from app import create_app, db
from app.models import Photo

# Create Flask app context
app = create_app()
app.app_context().push()

# Configuration
PHOTOS_DIR = 'app/static/images/photos'

def update_photo_dimensions():
    """
    Update existing photos with width and height information
    NOTE: This script is currently disabled until database migration is run to add width/height columns
    """
    print("This script is disabled until database migration is run to add width/height columns.")
    print("To enable:")
    print("1. Uncomment width and height columns in app/models.py")
    print("2. Run: flask db migrate -m 'Add width and height to Photo model'")
    print("3. Run: flask db upgrade")
    print("4. Uncomment the code in this script")
    return
    
    """
    # UNCOMMENT THIS CODE AFTER MIGRATION
    photos = Photo.query.all()
    updated_count = 0

    for photo in photos:
        if photo.width is not None and photo.height is not None:
            continue  # Skip if dimensions already set
            
        img_path = os.path.join(PHOTOS_DIR, photo.filename)
        if not os.path.exists(img_path):
            print(f"Warning: Image file not found for {photo.filename}")
            continue
            
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                photo.width = width
                photo.height = height
                updated_count += 1
                print(f"Updated dimensions for {photo.filename}: {width}x{height}")
        except Exception as e:
            print(f"Error getting dimensions for {photo.filename}: {e}")
    
    if updated_count > 0:
        db.session.commit()
        print(f"Updated dimensions for {updated_count} photos")
    else:
        print("No photos needed dimension updates")
    """

if __name__ == '__main__':
    update_photo_dimensions()
    print("Completed checking photo dimensions.") 