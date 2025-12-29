import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import
from app.app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User.query.filter_by(username='adminsauk119').first()
    
    if admin:
        print(f'Before: {admin.password}')
        
        # Hash the password
        hashed = generate_password_hash(admin.password)
        admin.password = hashed
        db.session.commit()
        
        print(f'After: {admin.password[:50]}...')
        print('✅ Admin password hashed successfully!')
    else:
        print('❌ Admin user not found!')
        print('Creating admin user...')
        
        # Create admin if doesn't exist
        admin = User(
            username='adminsauk119',
            password=generate_password_hash('bsf1802507'),
            role='admin',
            first_login=1
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created with hashed password!')