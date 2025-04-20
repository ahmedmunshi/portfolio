from app import create_app, db
from app.models import User
import sys

def list_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print("Current users:")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Admin: {user.is_admin}")

def make_admin(username):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found.")
            return
        
        user.is_admin = True
        db.session.commit()
        print(f"User '{username}' is now an admin.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_users()
    elif len(sys.argv) == 2:
        make_admin(sys.argv[1])
    else:
        print("Usage: python make_admin.py [username]")
        print("If username is provided, that user will be made an admin.")
        print("Otherwise, all users will be listed.") 