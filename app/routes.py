import os
import secrets
from datetime import datetime
from PIL import Image, ExifTags
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, abort, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import db
from app.forms import LoginForm, PhotoUploadForm, CategoryForm
from app.models import User, Photo, Category
import re

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def create_thumbnail(image, filename, size):
    img = Image.open(image)
    img.thumbnail(size)
    thumbnail_filename = f"thumb_{filename}"
    thumbnail_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
    
    # Use higher quality setting for JPEG files (95% quality)
    if filename.lower().endswith(('.jpg', '.jpeg')):
        img.save(thumbnail_path, quality=95, optimize=True)
    else:
        img.save(thumbnail_path, optimize=True)
    
    return thumbnail_filename

def extract_exif_data(image):
    """Extract EXIF data from image"""
    img = Image.open(image)
    exif_data = {}
    
    try:
        if hasattr(img, '_getexif') and img._getexif():
            exif = {
                ExifTags.TAGS[k]: v
                for k, v in img._getexif().items()
                if k in ExifTags.TAGS
            }
            
            # Camera info
            exif_data['camera_model'] = exif.get('Model', '')
            
            # Lens info
            exif_data['lens_model'] = exif.get('LensModel', '')
            
            # Settings
            if 'FocalLength' in exif:
                exif_data['focal_length'] = f"{exif['FocalLength']}mm"
            
            if 'ExposureTime' in exif:
                exposure = exif['ExposureTime']
                if isinstance(exposure, tuple):
                    exif_data['exposure_time'] = f"{exposure[0]}/{exposure[1]}s"
                else:
                    exif_data['exposure_time'] = f"{exposure}s"
            
            if 'FNumber' in exif:
                f_number = exif['FNumber']
                if isinstance(f_number, tuple):
                    exif_data['aperture'] = f"f/{f_number[0]/f_number[1]:.1f}"
                else:
                    exif_data['aperture'] = f"f/{f_number:.1f}"
            
            exif_data['iso'] = exif.get('ISOSpeedRatings', '')
            
            # Date taken
            if 'DateTimeOriginal' in exif:
                date_str = exif['DateTimeOriginal']
                try:
                    exif_data['date_taken'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    pass
    except Exception as e:
        current_app.logger.error(f"Error extracting EXIF data: {e}")
    
    return exif_data

def generate_slug(name):
    """Generate a URL-friendly slug from a name"""
    return re.sub(r'[^\w]+', '-', name.lower()).strip('-')

# Error handlers
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# Main routes
@main_bp.route('/')
def home():
    featured_photos = Photo.query.filter_by(featured=True).order_by(Photo.timestamp.desc()).limit(6).all()
    recent_photos = Photo.query.order_by(Photo.timestamp.desc()).limit(8).all()
    return render_template('home.html', featured_photos=featured_photos, recent_photos=recent_photos)

@main_bp.route('/gallery')
def gallery():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    is_ajax = request.args.get('ajax', 0, type=int)
    
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        photos = category.photos.order_by(Photo.timestamp.desc()).paginate(page=page, per_page=12)
        active_category = category.id
    else:
        photos = Photo.query.order_by(Photo.timestamp.desc()).paginate(page=page, per_page=12)
        active_category = None
    
    categories = Category.query.order_by(Category.name).all()
    
    # If AJAX request, return partial template with only the gallery content
    if is_ajax:
        return render_template('partials/photo_grid.html', 
                              photos=photos,
                              categories=categories, 
                              active_category=active_category)
    
    # For normal request, return full gallery page
    return render_template('gallery.html', 
                          photos=photos, 
                          categories=categories, 
                          active_category=active_category)

@main_bp.route('/photo/<int:id>')
def photo_detail(id):
    photo = Photo.query.get_or_404(id)
    
    # If user is admin, get all categories for the edit form
    all_categories = None
    if current_user.is_authenticated and current_user.is_admin:
        all_categories = Category.query.order_by(Category.name).all()
    
    return render_template('photo_detail.html', photo=photo, all_categories=all_categories)

# Auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        # Set permanent session if remember is checked
        if form.remember_me.data:
            session.permanent = True
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.home')
        
        # Flash message for successful login
        flash(f'Welcome, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    # Clear all session data to prevent auth issues
    session.clear()
    return redirect(url_for('main.home'))

# Admin helper to check if user is admin
def check_admin():
    if not current_user.is_authenticated:
        flash('Please log in to access the admin area.', 'error')
        return False
    
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'error')
        return False
    
    return True

# Admin routes
@admin_bp.route('/')
@login_required
def index():
    if not check_admin():
        return redirect(url_for('main.home'))
    
    photos = Photo.query.order_by(Photo.timestamp.desc()).all()
    return render_template('admin/index.html', photos=photos)

@admin_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not check_admin():
        return redirect(url_for('main.home'))
    
    form = PhotoUploadForm()
    
    if form.validate_on_submit():
        file = form.photo.data
        if file and allowed_file(file.filename):
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            random_hex = secrets.token_hex(8)
            _, file_extension = os.path.splitext(filename)
            filename = f"{random_hex}{file_extension}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Extract EXIF data before saving
            exif_data = extract_exif_data(file)
            
            # Save original photo
            file.save(file_path)
            
            # Create thumbnail
            thumbnail_filename = create_thumbnail(file_path, filename, current_app.config['THUMBNAIL_SIZE'])
            
            # Save to database
            photo = Photo(
                title=form.title.data,
                description=form.description.data,
                filename=filename,
                thumbnail=thumbnail_filename,
                featured=form.featured.data,
                author=current_user,
                **exif_data
            )
            
            # Add selected categories
            for category_id in form.categories.data:
                category = Category.query.get(category_id)
                if category:
                    photo.categories.append(category)
            
            db.session.add(photo)
            db.session.commit()
            
            flash('Photo uploaded successfully!', 'success')
            return redirect(url_for('admin.index'))
    
    return render_template('admin/upload.html', form=form)

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if not check_admin():
        return redirect(url_for('main.home'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            slug=generate_slug(form.name.data)
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin.categories'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', form=form, categories=categories)

@admin_bp.route('/toggle_featured/<int:id>', methods=['POST'])
@login_required
def toggle_featured(id):
    if not check_admin():
        return jsonify(success=False, error='Permission denied'), 403
    
    photo = Photo.query.get_or_404(id)
    photo.featured = not photo.featured
    db.session.commit()
    
    return jsonify(success=True, featured=photo.featured)

@admin_bp.route('/delete_photo/<int:id>', methods=['POST'])
@login_required
def delete_photo(id):
    if not check_admin():
        return redirect(url_for('main.home'))
    
    photo = Photo.query.get_or_404(id)
    
    # Delete image files
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename))
        os.remove(os.path.join(current_app.config['THUMBNAIL_FOLDER'], photo.thumbnail))
    except Exception as e:
        current_app.logger.error(f"Error deleting files: {e}")
    
    # Delete from database
    db.session.delete(photo)
    db.session.commit()
    
    flash('Photo deleted successfully', 'success')
    return redirect(url_for('admin.index'))

@admin_bp.route('/update_categories/<int:id>', methods=['POST'])
@login_required
def update_categories(id):
    if not check_admin():
        return jsonify(success=False, error='Permission denied'), 403
    
    photo = Photo.query.get_or_404(id)
    categories = request.form.getlist('categories')
    
    # Clear existing categories
    photo.categories = []
    
    # Add selected categories
    for category_id in categories:
        category = Category.query.get(int(category_id))
        if category:
            photo.categories.append(category)
    
    db.session.commit()
    
    # If request is AJAX, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    
    # Otherwise redirect back to photo detail page
    flash('Categories updated successfully', 'success')
    return redirect(url_for('main.photo_detail', id=photo.id))

@admin_bp.route('/manage_featured', methods=['GET', 'POST'])
@login_required
def manage_featured():
    if not check_admin():
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Clear all featured flags
        Photo.query.update({Photo.featured: False})
        
        # Set featured flags based on form submission
        featured_ids = request.form.getlist('featured_photos')
        if featured_ids:
            Photo.query.filter(Photo.id.in_([int(id) for id in featured_ids])).update(
                {Photo.featured: True}, synchronize_session=False
            )
        
        db.session.commit()
        flash('Featured photos updated successfully', 'success')
        return redirect(url_for('admin.manage_featured'))
    
    # Get all photos, ordered by most recent first
    photos = Photo.query.order_by(Photo.timestamp.desc()).all()
    return render_template('admin/manage_featured.html', photos=photos)

@admin_bp.route('/regenerate_thumbnails')
@login_required
def regenerate_thumbnails():
    if not check_admin():
        return redirect(url_for('main.home'))
    
    # Get all photos
    photos = Photo.query.all()
    regenerated_count = 0
    
    for photo in photos:
        # Get file path for original image
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
        
        # Check if original image exists
        if os.path.exists(file_path):
            try:
                # Delete old thumbnail if exists
                old_thumbnail_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], photo.thumbnail)
                if os.path.exists(old_thumbnail_path):
                    os.remove(old_thumbnail_path)
                
                # Generate new thumbnail
                thumbnail_filename = create_thumbnail(
                    file_path, 
                    photo.filename, 
                    current_app.config['THUMBNAIL_SIZE']
                )
                
                # Update database with new thumbnail filename if different
                if thumbnail_filename != photo.thumbnail:
                    photo.thumbnail = thumbnail_filename
                    db.session.add(photo)
                
                regenerated_count += 1
            except Exception as e:
                current_app.logger.error(f"Error regenerating thumbnail for {photo.filename}: {e}")
    
    # Commit all changes
    db.session.commit()
    
    flash(f'Successfully regenerated {regenerated_count} thumbnails with higher quality.', 'success')
    return redirect(url_for('admin.index')) 