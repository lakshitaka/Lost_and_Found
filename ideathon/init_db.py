from app import app, db, User

# Create tables
with app.app_context():
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create new tables
    
    # Create admin user
    admin = User(
        name='Admin',
        email='admin@kongu.edu',
        password='admin123',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print("Database initialized and admin user created!")
