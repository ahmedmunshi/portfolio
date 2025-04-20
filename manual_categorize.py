import os
import webbrowser
import time
from flask import url_for
from app import create_app, db
from app.models import Photo, Category

# Create Flask app context
app = create_app()
app.app_context().push()

def categorize_with_preview():
    """Categorize photos with preview capability"""
    
    # Get the Car and Street categories (or create them if they don't exist)
    car_category = Category.query.filter_by(name='Car Photography').first()
    if not car_category:
        car_category = Category(name='Car Photography', slug='car-photography')
        db.session.add(car_category)
        db.session.commit()
    
    street_category = Category.query.filter_by(name='Street Photography').first()
    if not street_category:
        street_category = Category(name='Street Photography', slug='street-photography')
        db.session.add(street_category)
        db.session.commit()
    
    # Get all photos
    photos = Photo.query.all()
    
    if not photos:
        print("No photos found in the database.")
        return
    
    print(f"Found {len(photos)} photos to categorize.")
    print("For each photo, enter 'c' for Car, 's' for Street, or press Enter to skip.")
    print("You can also type 'q' at any time to quit.\n")
    
    # For each photo
    for i, photo in enumerate(photos, 1):
        # Get photo file path
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        photo_url = f"http://127.0.0.1:5000/static/images/photos/{photo.filename}"
        
        # Display info about the photo
        print(f"\n[{i}/{len(photos)}] Photo: {photo.title}")
        print(f"Filename: {photo.filename}")
        
        # Show current categories
        current_categories = [cat.name for cat in photo.categories]
        print(f"Current categories: {', '.join(current_categories) if current_categories else 'None'}")
        
        # Open the image in the default browser
        print(f"Opening photo in browser: {photo_url}")
        webbrowser.open(photo_url)
        
        # Wait for user input
        while True:
            user_input = input("Categorize as (c)ar, (s)treet, or [Enter] to skip (q to quit): ").lower()
            
            if user_input == 'q':
                print("Exiting categorization.")
                return
            
            elif user_input == 'c':
                # Remove from street if present
                if street_category in photo.categories:
                    photo.categories.remove(street_category)
                # Add to car if not present
                if car_category not in photo.categories:
                    photo.categories.append(car_category)
                db.session.commit()
                print(f"Categorized as Car Photography.")
                break
                
            elif user_input == 's':
                # Remove from car if present
                if car_category in photo.categories:
                    photo.categories.remove(car_category)
                # Add to street if not present
                if street_category not in photo.categories:
                    photo.categories.append(street_category)
                db.session.commit()
                print(f"Categorized as Street Photography.")
                break
                
            elif user_input == '':
                print(f"Skipping photo.")
                break
                
            else:
                print("Invalid input. Please try again.")
    
    print("\nCategorization complete.")
    
    # Count photos in each category
    car_count = len(car_category.photos.all())
    street_count = len(street_category.photos.all())
    
    print(f"\nFinal counts:")
    print(f"Car Photography: {car_count} photos")
    print(f"Street Photography: {street_count} photos")

if __name__ == "__main__":
    # Ensure Flask is running
    print("Make sure your Flask application is running at http://127.0.0.1:5000")
    print("Press Enter when ready...")
    input()
    
    # Start categorization
    categorize_with_preview() 