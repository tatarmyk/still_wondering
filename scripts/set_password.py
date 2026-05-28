#!/usr/bin/env python3
"""Offline script to set the author password.

Usage:
    python scripts/set_password.py [username]

This creates/updates the author's password hash in the database.
Must be run from the project root directory.
"""
import sys
import os
import getpass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argon2 import PasswordHasher
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.models import get_db, Author


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"

    password = getpass.getpass(f"Enter password for '{username}': ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Error: passwords do not match.")
        sys.exit(1)

    if len(password) < 8:
        print("Error: password must be at least 8 characters.")
        sys.exit(1)

    ph = PasswordHasher()
    hashed = ph.hash(password)

    app = create_app()
    with app.app_context():
        db = get_db()
        try:
            author = db.query(Author).filter_by(username=username).first()
            if author:
                author.password_hash = hashed
                print(f"Updated password for '{username}'.")
            else:
                author = Author(username=username, password_hash=hashed)
                db.add(author)
                print(f"Created author '{username}'.")
            db.commit()
        finally:
            db.close()

    print("Done.")


if __name__ == "__main__":
    main()
