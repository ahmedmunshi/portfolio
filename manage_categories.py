import os
import sys
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

def assign_photos_to_category(category_name, keywords):
    """Assign photos to a category based on filename keywords"""
    # Create or get the category
    category = create_category(category_name)
    
    # Get all photos
    photos = Photo.query.all()
    count = 0
    
    for photo in photos:
        filename_lower = photo.filename.lower()
        title_lower = photo.title.lower() if photo.title else ""
        
        # Check if any keyword is in the filename or title
        if any(keyword.lower() in filename_lower or keyword.lower() in title_lower for keyword in keywords):
            # Check if photo is already in this category
            if category not in photo.categories:
                photo.categories.append(category)
                count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Assigned {count} photos to category '{category_name}'")
    else:
        print(f"No photos matched the keywords for category '{category_name}'")

def list_all_photos():
    """List all photos with their filenames and titles"""
    photos = Photo.query.all()
    print("\nAll Photos:")
    print("=" * 80)
    for photo in photos:
        print(f"ID: {photo.id} | Filename: {photo.filename} | Title: {photo.title}")
    print("=" * 80)

def create_default_categories():
    """Create default categories for the portfolio"""
    # Create street photography category
    street = create_category("Street Photography")
    
    # Create car photography category
    cars = create_category("Car Photography")
    
    # You can add more categories as needed
    portrait = create_category("Portrait")
    landscape = create_category("Landscape")
    architecture = create_category("Architecture")
    
    print("\nCreated the following categories:")
    categories = Category.query.all()
    for category in categories:
        print(f"- {category.name} (slug: {category.slug})")

def categorize_photos_manually():
    """Set up specific assignments based on keywords"""
    # For street photography, look for keywords
    assign_photos_to_category("Street Photography", ["street", "city", "urban", "people"])
    
    # For car photography
    assign_photos_to_category("Car Photography", ["car", "auto", "vehicle", "wheel"])
    
    # For landscapes
    assign_photos_to_category("Landscape", ["landscape", "mountain", "nature", "sky", "sunset"])
    
    # For architecture
    assign_photos_to_category("Architecture", ["building", "architecture", "structure"])
    
    # For portraits
    assign_photos_to_category("Portrait", ["portrait", "person", "face", "selfie"])

def interactive_categorize():
    """Interactively categorize photos"""
    print("\nInteractive Categorization")
    print("=" * 80)
    print("This will help you manually assign categories to each photo")
    
    # Get all categories
    categories = Category.query.all()
    if not categories:
        print("No categories found. Creating defaults first...")
        create_default_categories()
        categories = Category.query.all()
    
    # Display categories with numbers
    print("\nAvailable Categories:")
    for idx, category in enumerate(categories, 1):
        print(f"{idx}. {category.name}")
    
    # Get all photos
    photos = Photo.query.all()
    
    for photo in photos:
        print(f"\nPhoto: {photo.title} (filename: {photo.filename})")
        
        # Show current categories
        if photo.categories:
            current_cats = ", ".join([cat.name for cat in photo.categories])
            print(f"Current categories: {current_cats}")
        else:
            print("Current categories: None")
        
        print("\nChoose categories (comma-separated numbers, or press Enter to skip):")
        user_input = input("> ")
        
        if user_input.strip():
            # Clear existing categories
            photo.categories = []
            
            # Add selected categories
            for choice in user_input.split(","):
                try:
                    idx = int(choice.strip()) - 1
                    if 0 <= idx < len(categories):
                        photo.categories.append(categories[idx])
                        print(f"Added {categories[idx].name}")
                    else:
                        print(f"Invalid category number: {choice}")
                except ValueError:
                    print(f"Invalid input: {choice}")
            
            db.session.commit()
            print("Categories updated.")

def condense_categories():
    """Condense all categories to only Car and Street"""
    
    # Get the Car and Street categories
    car_category = Category.query.filter_by(name='Car Photography').first()
    street_category = Category.query.filter_by(name='Street Photography').first()
    
    # Ensure these categories exist
    if not car_category:
        car_category = Category(name='Car Photography', slug='car-photography')
        db.session.add(car_category)
        db.session.commit()
        print("Created 'Car Photography' category")
    
    if not street_category:
        street_category = Category(name='Street Photography', slug='street-photography')
        db.session.add(street_category)
        db.session.commit()
        print("Created 'Street Photography' category")
    
    # Get all other categories
    other_categories = Category.query.filter(
        Category.id.notin_([car_category.id, street_category.id])
    ).all()
    
    # Process photos from other categories
    for category in other_categories:
        print(f"Processing photos from '{category.name}'...")
        
        # Get all photos in this category
        photos = category.photos.all()
        
        for photo in photos:
            # Check if photo already belongs to Car or Street
            in_car = car_category in photo.categories
            in_street = street_category in photo.categories
            
            # If not in either, assign based on category name
            if not (in_car or in_street):
                # Simple heuristic: if category name contains 'car', 'auto', etc. assign to car
                if any(term in category.name.lower() for term in ['car', 'auto', 'vehicle']):
                    photo.categories.append(car_category)
                    print(f"  - Assigned photo {photo.id} ({photo.title}) to Car Photography")
                else:
                    # Otherwise assign to street
                    photo.categories.append(street_category)
                    print(f"  - Assigned photo {photo.id} ({photo.title}) to Street Photography")
        
        # After processing photos, delete the category
        print(f"Deleting category '{category.name}'")
        db.session.delete(category)
    
    # Commit all changes
    db.session.commit()
    print("Category consolidation complete")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Run interactive mode
        interactive_categorize()
    else:
        # Non-interactive mode
        print("Creating categories and auto-assigning photos...")
        create_default_categories()
        categorize_photos_manually()
        print("\nTo manually categorize all photos, run:")
        print("python manage_categories.py --interactive")
    
    print("\nCompleted. You can now view categorized photos on the website.")
    
    condense_categories()
    
    # Verify only two categories remain
    categories = Category.query.all()
    print("\nRemaining categories:")
    for category in categories:
        print(f"- {category.name}") 