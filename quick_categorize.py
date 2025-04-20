import os
import re
from app import create_app, db
from app.models import Photo, Category

# Create Flask app context
app = create_app()
app.app_context().push()

def create_category(name):
    """Create a category if it doesn't exist"""
    # Create a slug from the name (lowercase, replace spaces with hyphens)
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[\s-]+', '-', slug).strip('-')
    
    # Check if category exists
    category = Category.query.filter_by(slug=slug).first()
    if not category:
        category = Category(name=name, slug=slug)
        db.session.add(category)
        db.session.commit()
        print(f"Created category: {name}")
    return category

def assign_all_street_photos():
    """Assign all photos to the Street Photography category"""
    # Get the Street Photography category
    street_category = create_category("Street Photography")
    
    # Get all photos
    photos = Photo.query.all()
    count = 0
    
    for photo in photos:
        # Skip if photo already has this category
        if street_category in photo.categories:
            continue
        
        photo.categories.append(street_category)
        count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Assigned {count} photos to Street Photography category")
    else:
        print("No photos were assigned to Street Photography category")

def assign_all_car_photos():
    """Assign all photos to the Car Photography category"""
    # Get the Car Photography category
    car_category = create_category("Car Photography")
    
    # Get all photos
    photos = Photo.query.all()
    count = 0
    
    for photo in photos:
        # Skip if photo already has this category
        if car_category in photo.categories:
            continue
        
        photo.categories.append(car_category)
        count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Assigned {count} photos to Car Photography category")
    else:
        print("No photos were assigned to Car Photography category")

def assign_street_photos_by_keyword():
    """Assign street photos based on keywords in filename"""
    street_keywords = [
        "toronto", "light", "graffiti", "staircase", "parkinggarage",
        "skating", "waiting", "bus", "ttc", "train", "path", "night"
    ]
    
    # Get the Street Photography category
    street_category = create_category("Street Photography")
    
    # Get all photos
    photos = Photo.query.all()
    count = 0
    
    for photo in photos:
        filename_lower = photo.filename.lower()
        
        # Check if any street keyword is in the filename
        if any(keyword.lower() in filename_lower for keyword in street_keywords):
            # Skip if photo already has this category
            if street_category in photo.categories:
                continue
            
            photo.categories.append(street_category)
            print(f"Assigning '{photo.filename}' to Street Photography")
            count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Assigned {count} photos to Street Photography category")
    else:
        print("No photos matched street photography keywords")

def assign_car_photos_by_keyword():
    """Assign car photos based on keywords in filename"""
    car_keywords = [
        "nsx", "bmw", "porsche", "rwb", "car", "redrwb", "greenrwb", "whiterwb",
        "oliver", "classics", "undergroundsyndicate"
    ]
    
    # Get the Car Photography category
    car_category = create_category("Car Photography")
    
    # Get all photos
    photos = Photo.query.all()
    count = 0
    
    for photo in photos:
        filename_lower = photo.filename.lower()
        
        # Check if any car keyword is in the filename
        if any(keyword.lower() in filename_lower for keyword in car_keywords):
            # Skip if photo already has this category
            if car_category in photo.categories:
                continue
            
            photo.categories.append(car_category)
            print(f"Assigning '{photo.filename}' to Car Photography")
            count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Assigned {count} photos to Car Photography category")
    else:
        print("No photos matched car photography keywords")

def clear_all_categories():
    """Remove all photos from all categories"""
    # Get all photos
    photos = Photo.query.all()
    count = 0
    
    for photo in photos:
        if photo.categories:
            photo.categories = []
            count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Cleared categories for {count} photos")
    else:
        print("No photos had categories to clear")

def print_menu():
    """Print the menu options"""
    print("\nQUICK CATEGORIZE")
    print("=" * 80)
    print("1. Assign all photos to Street Photography")
    print("2. Assign all photos to Car Photography")
    print("3. Assign photos to Street Photography by keywords")
    print("4. Assign photos to Car Photography by keywords")
    print("5. Clear all categories")
    print("6. Quit")
    print("=" * 80)

if __name__ == "__main__":
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ")
        
        if choice == "1":
            assign_all_street_photos()
        elif choice == "2":
            assign_all_car_photos()
        elif choice == "3":
            assign_street_photos_by_keyword()
        elif choice == "4":
            assign_car_photos_by_keyword()
        elif choice == "5":
            clear_all_categories()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")
    
    print("Categories have been updated. You can now view your organized portfolio.") 