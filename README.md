# Photography Portfolio

A stunning photography portfolio website built with Flask, featuring full-screen galleries, EXIF data extraction, and an admin panel for photo management.

## Features

- Minimalist black and white design with smooth animations
- Full-screen image gallery with lightbox functionality
- Mobile-responsive design
- Dynamic category filtering
- Admin panel for photo uploads
- Automatic thumbnail generation
- EXIF data extraction
- Featured photos section
- Smooth page transitions
- Lazy loading for images

## Technology Stack

- **Backend**: Flask with Python
- **Database**: SQLAlchemy with SQLite
- **Frontend**: TailwindCSS, custom CSS animations, PhotoSwipe for image gallery
- **Image Processing**: Pillow for thumbnails and EXIF data

## Installation

1. Clone the repository

```bash
git clone <repository-url>
cd photography_portfolio
```

2. Create a virtual environment and activate it

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Initialize the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Create an admin user

```bash
python -c "from app import db, create_app; from app.models import User; app = create_app(); app.app_context().push(); admin = User(username='admin', is_admin=True); admin.set_password('your_secure_password'); db.session.add(admin); db.session.commit(); print('Admin user created!')"
```

## Usage

1. Start the development server

```bash
python run.py
```

2. Access the website at `http://localhost:5000`

3. Login to the admin panel at `http://localhost:5000/auth/login` using the credentials you created

## Project Structure

```
photography_portfolio/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # All route handlers
│   ├── models.py            # SQLAlchemy models
│   ├── forms.py             # WTForms for uploads
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css     # Main styles
│   │   │   └── animations.css# Animation definitions
│   │   ├── js/
│   │   │   ├── main.js      # Main JavaScript
│   │   │   └── gallery.js   # Gallery functionality
│   │   └── images/
│   │       ├── photos/      # Original uploads
│   │       └── thumbnails/  # Generated thumbnails
│   └── templates/
│       ├── base.html        # Base template with nav
│       ├── home.html        # Homepage with hero
│       ├── gallery.html     # Photo grid
│       ├── photo_detail.html# Single photo view
│       └── admin/
│           └── upload.html  # Admin upload form
├── config.py                # App configuration
├── run.py                   # Application entry point
└── requirements.txt         # Python dependencies
```

## Customization

### Changing Theme Colors

Edit the CSS variables in `app/static/css/main.css`:

```css
:root {
    --black: #000000;
    --dark-gray: #111111;
    --medium-gray: #333333;
    --light-gray: #666666;
    --white: #ffffff;
    --transition-smooth: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Adding Categories

1. Login to the admin panel
2. Navigate to the Categories section
3. Add new categories as needed

### Customizing Image Sizes

Edit the configuration in `config.py`:

```python
THUMBNAIL_SIZE = (400, 400)
MAX_IMAGE_SIZE = (2000, 2000)
```

## License

[MIT License](LICENSE) 